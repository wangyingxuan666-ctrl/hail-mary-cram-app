"""RAG service for retrieval-augmented generation."""
from typing import Optional

from services.vector_store import similarity_search
from services.document_loader import get_all_materials, get_all_exams


def retrieve_context(query: str, k: int = 5) -> str:
    """Retrieve relevant course material chunks for a query."""
    results = similarity_search(query, k=k)

    if not results:
        return "（暂无相关课件内容）"

    context_parts = []
    for i, r in enumerate(results):
        source = r["metadata"].get("source", "unknown")
        context_parts.append(f"[来源: {source}]\n{r['content']}")

    return "\n\n---\n\n".join(context_parts)


def get_materials_context() -> str:
    """Get summary of all uploaded materials."""
    materials = get_all_materials()
    if not materials:
        return "（未上传课件）"
    parts = [f"- {m['filename']} ({m['page_count']}页)" for m in materials]
    return "\n".join(parts)


def get_exams_summary() -> str:
    """Get summary of all uploaded exam papers."""
    exams = get_all_exams()
    if not exams:
        return "（未上传真题）"
    parts = []
    for e in exams:
        years = _extract_years(e.get("text", ""))
        parts.append(f"- {e['filename']} ({e['page_count']}页, 年份: {', '.join(years) if years else '未知'})")
    return "\n".join(parts)


def _extract_years(text: str) -> list[str]:
    """Try to extract years from exam text."""
    import re
    # Match common year patterns like 2023, 2024, etc.
    years = set()
    for m in re.finditer(r'\b(20\d{2})\b', text):
        years.add(m.group(1))
    return sorted(years)
