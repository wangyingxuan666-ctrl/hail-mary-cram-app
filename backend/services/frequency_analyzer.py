"""Frequency analysis service using LLM to extract exam topics."""
import json
import re
from datetime import datetime

from openai import OpenAI

from config import settings
from models.exam import TopicFrequency, FrequencyTable
from services.document_loader import get_all_exams
from prompts.frequency_analysis import FREQUENCY_ANALYSIS_SYSTEM, FREQUENCY_ANALYSIS_USER


_client: OpenAI = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


def _calculate_priority(frequency_pct: float) -> str:
    if frequency_pct >= 50:
        return "🔴"
    elif frequency_pct >= 30:
        return "🟠"
    elif frequency_pct >= 20:
        return "🟡"
    else:
        return "🟢"


def _parse_llm_json_response(response_text: str) -> list[dict]:
    """Parse LLM response, trying to extract JSON array."""
    # Try direct parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find bare JSON array
    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return []


async def generate_frequency_table(course_name: str = "") -> FrequencyTable:
    """Scan all exam papers and generate a frequency table using LLM."""
    exams = get_all_exams()

    if not exams:
        return FrequencyTable(course_name=course_name or "未知课程")

    # Prepare exam contents for LLM
    exam_contents = []
    years_set = set()
    for exam in exams:
        text = exam.get("text", exam.get("content_preview", ""))
        # Limit text per exam to avoid token overflow
        if len(text) > 8000:
            text = text[:8000] + "...(内容已截断)"
        exam_contents.append(f"### {exam['filename']}\n{text}")

    combined = "\n\n".join(exam_contents)

    # Call LLM
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": FREQUENCY_ANALYSIS_SYSTEM},
            {"role": "user", "content": FREQUENCY_ANALYSIS_USER.format(exam_contents=combined)},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw_output = response.choices[0].message.content or ""
    topic_entries = _parse_llm_json_response(raw_output)

    # Extract all years from exam filenames
    import re
    for exam in exams:
        for m in re.finditer(r'\b(20\d{2})\b', exam["filename"]):
            years_set.add(m.group(1))

    total_years = len(years_set) if years_set else 1

    # Aggregate topics by name
    topic_map: dict[str, dict] = {}
    for entry in topic_entries:
        name = entry.get("topic_name", "未知考点")
        year = str(entry.get("year", ""))
        q_num = entry.get("question_number", "")
        if name not in topic_map:
            topic_map[name] = {"years": set(), "questions": []}
        if year:
            topic_map[name]["years"].add(year)
        if q_num:
            topic_map[name]["questions"].append(f"{year}-{q_num}" if year else q_num)

    # Build frequency table
    topics = []
    for name, data in topic_map.items():
        freq_count = len(data["years"])
        freq_pct = round((freq_count / total_years) * 100, 1)
        priority = _calculate_priority(freq_pct)
        topics.append(TopicFrequency(
            topic_name=name,
            years=sorted(data["years"]),
            frequency_count=freq_count,
            total_years=total_years,
            frequency_pct=freq_pct,
            priority=priority,
            related_questions=data["questions"],
        ))

    # Sort by frequency descending
    topics.sort(key=lambda t: t.frequency_count, reverse=True)

    # Build CLAUDE.md content and save
    _save_analysis({
        "course_name": course_name,
        "total_exam_years": total_years,
        "topics": [t.model_dump() for t in topics],
        "generated_at": datetime.now().isoformat(),
    })

    return FrequencyTable(
        course_name=course_name or "未知课程",
        total_exam_years=total_years,
        topics=topics,
        generated_at=datetime.now(),
    )


def get_cached_frequency_table() -> FrequencyTable:
    """Get the cached frequency table."""
    data = _load_analysis()
    if not data or not data.get("topics"):
        return FrequencyTable()

    return FrequencyTable(
        course_name=data.get("course_name", ""),
        total_exam_years=data.get("total_exam_years", 0),
        topics=[TopicFrequency(**t) for t in data["topics"]],
        generated_at=datetime.fromisoformat(data.get("generated_at", datetime.now().isoformat())),
    )


def _save_analysis(data: dict) -> None:
    """Save analysis results to disk."""
    from config import settings
    p = settings.get_data_path("analysis.json")
    import json as _json
    p.write_text(_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also write CLAUDE.md
    _write_claude_md(data)


def _load_analysis() -> dict:
    from config import settings
    p = settings.get_data_path("analysis.json")
    import json as _json
    if p.exists():
        return _json.loads(p.read_text(encoding="utf-8"))
    return {}


def _write_claude_md(data: dict) -> None:
    """Write CLAUDE.md with frequency table and document index."""
    from config import settings
    from services.document_loader import get_all_documents

    lines = [
        f"# {data.get('course_name', '未知课程')} — 复习知识库",
        "",
        "## 文件索引",
        "| 文件 | 类型 | 页数 | 优先级 |",
        "|------|------|------|--------|",
    ]

    docs = get_all_documents()
    for d in docs:
        priority = "⭐⭐⭐" if d["doc_type"] == "exam" else "⭐⭐"
        lines.append(f"| {d['filename']} | {d['doc_type']} | {d['page_count']} | {priority} |")

    lines.extend([
        "",
        "## 历年考点频率",
        "| 考点 | 出现年份 | 频率 | 优先级 |",
        "|------|----------|------|--------|",
    ])

    for t in data.get("topics", []):
        years_str = "/".join(t["years"])
        freq_str = f"{t['frequency_count']}/{t['total_years']}"
        lines.append(f"| {t['topic_name']} | {years_str} | {freq_str} | {t['priority']} |")

    p = settings.get_data_path("CLAUDE.md")
    p.write_text("\n".join(lines), encoding="utf-8")
