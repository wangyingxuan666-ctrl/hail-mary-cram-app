"""Export service for generating markdown study documents."""
import json
from datetime import datetime
from pathlib import Path

from config import settings
from services.frequency_analyzer import get_cached_frequency_table
from services.memory_service import get_memory_status
from services.document_loader import get_all_documents


EXPORT_DIR = settings.get_data_path("exports")


def generate_single_exam(exam_year: str = "") -> str:
    """Generate single exam walkthrough markdown."""
    freq = get_cached_frequency_table()
    docs = get_all_documents()

    lines = [
        f"# {exam_year or '历年'}真题讲解",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 考点频率概览",
        "",
        "| 考点 | 频率 | 优先级 |",
        "|------|------|--------|",
    ]

    if freq.topics:
        for t in freq.topics:
            lines.append(f"| {t.topic_name} | {t.frequency_count}/{t.total_years} | {t.priority} |")
    else:
        lines.append("| 暂无数据 | - | - |")

    lines.extend([
        "",
        "## 逐题讲解",
        "",
        "*在此与 AI 逐题对话后，讲解内容将自动填充到此部分。*",
        "",
        "---",
        "",
        "## 文件来源",
        "",
    ])

    for d in docs:
        lines.append(f"- {d['filename']} ({d['doc_type']}, {d['page_count']}页)")

    return "\n".join(lines)


def generate_cross_year() -> str:
    """Generate cross-year comparison + cheat sheet."""
    freq = get_cached_frequency_table()
    memory = get_memory_status()

    lines = [
        "# 跨卷对照速记卡",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 高频考点（跨年重复）",
        "",
        "| 考点 | 出现年份 | 优先级 | 掌握状态 |",
        "|------|----------|--------|----------|",
    ]

    memory_map = {e.topic: e.status for e in memory.entries}

    if freq.topics:
        for t in freq.topics:
            if t.frequency_count >= 2:  # multi-year = high priority cross-year
                status = memory_map.get(t.topic_name, "未开始")
                status_emoji = {"mastered": "✅", "confused": "⚠️", "learning": "📖"}.get(status, "⬜")
                lines.append(f"| {t.topic_name} | {'/'.join(t.years)} | {t.priority} | {status_emoji} {status} |")

    lines.extend([
        "",
        "## 速记要点",
        "",
        "*逐题讲解完成后，浓缩要点将填充到此部分。*",
        "",
        "## 选题策略",
        "",
        "### 必选题",
        "",
        "### 备选题",
        "",
        "### 可跳过",
        "",
        "---",
        "",
        "> 考场速记卡 — 考前 5 分钟扫一遍",
    ])

    return "\n".join(lines)


def generate_gap_prediction(year: str = "") -> str:
    """Generate gap prediction for next exam."""
    freq = get_cached_frequency_table()
    year_str = year or str(datetime.now().year)

    lines = [
        f"# 补漏预测_{year_str}",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 低频/未考考点",
        "",
        "以下考点尚未在历年真题中高频出现，但可能在未来考试中出现：",
        "",
        "| 考点 | 历史频率 | 预测理由 |",
        "|------|----------|----------|",
    ]

    if freq.topics:
        for t in freq.topics:
            if t.frequency_pct < 30:
                reason = "近年未出现，可能轮换" if len(t.years) < 2 else "低频但稳定"
                lines.append(f"| {t.topic_name} | {t.frequency_count}/{t.total_years} ({t.frequency_pct}%) | {reason} |")
    else:
        lines.append("| 暂无数据 | - | - |")

    lines.extend([
        "",
        "## 预测新增考点",
        "",
        "*基于行业趋势和教学重点的变化，AI 将在此列出可能的出题方向。*",
        "",
        "---",
        "",
        "## 1 页 A4 极简终极版",
        "",
        "（考前 30 秒扫一遍）",
        "",
        "### 核心公式/概念",
        "",
        "### 最易混淆的 3 组概念",
        "",
        "### 必背金句",
    ])

    return "\n".join(lines)


def save_export(filename: str, content: str) -> str:
    """Save export content to disk and return the filename."""
    filepath = EXPORT_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def list_exports() -> list[dict]:
    """List all exported files."""
    if not EXPORT_DIR.exists():
        return []
    exports = []
    for f in EXPORT_DIR.iterdir():
        if f.is_file():
            exports.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
            })
    return sorted(exports, key=lambda x: x["created_at"], reverse=True)
