"""Memory service for tracking user mastery progress."""
import json
from datetime import datetime

from config import settings
from models.memory import MemoryEntry, MemoryStatus


def _get_memory_path():
    return settings.get_data_path("memory.json")


def _load_memory() -> dict:
    p = _get_memory_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"entries": {}}


def _save_memory(data: dict) -> None:
    _get_memory_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_memory_status() -> MemoryStatus:
    """Get current mastery tracking status."""
    data = _load_memory()
    entries_dict = data.get("entries", {})
    entries = []
    mastered = 0
    confused = 0

    for topic_name, entry_data in entries_dict.items():
        entry = MemoryEntry(
            topic=topic_name,
            status=entry_data.get("status", "learning"),
            notes=entry_data.get("notes", ""),
            last_reviewed=datetime.fromisoformat(entry_data["last_reviewed"])
                if entry_data.get("last_reviewed") else datetime.now(),
        )
        entries.append(entry)
        if entry.status == "mastered":
            mastered += 1
        elif entry.status == "confused":
            confused += 1

    return MemoryStatus(
        entries=entries,
        mastered_count=mastered,
        confused_count=confused,
        total_topics=len(entries),
    )


def update_memory(topic: str, status: str, notes: str = "") -> MemoryEntry:
    """Update mastery status for a topic."""
    data = _load_memory()
    if "entries" not in data:
        data["entries"] = {}

    data["entries"][topic] = {
        "status": status,
        "notes": notes,
        "last_reviewed": datetime.now().isoformat(),
    }

    _save_memory(data)

    return MemoryEntry(
        topic=topic,
        status=status,
        notes=notes,
        last_reviewed=datetime.now(),
    )


def delete_memory_entry(topic: str) -> bool:
    """Remove a memory entry."""
    data = _load_memory()
    if topic in data.get("entries", {}):
        del data["entries"][topic]
        _save_memory(data)
        return True
    return False
