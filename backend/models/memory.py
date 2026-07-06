from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class MemoryEntry(BaseModel):
    topic: str
    status: Literal["mastered", "confused", "learning"] = "learning"
    notes: str = ""
    last_reviewed: datetime = Field(default_factory=datetime.now)


class MemoryStatus(BaseModel):
    entries: list[MemoryEntry] = []
    mastered_count: int = 0
    confused_count: int = 0
    total_topics: int = 0


class UpdateMemoryRequest(BaseModel):
    topic: str
    status: Literal["mastered", "confused", "learning"]
    notes: str = ""
