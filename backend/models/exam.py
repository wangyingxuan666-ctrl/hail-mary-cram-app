from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class TopicFrequency(BaseModel):
    topic_name: str
    years: list[str] = []
    frequency_count: int = 0
    total_years: int = 0
    frequency_pct: float = 0.0
    priority: Literal["🔴", "🟠", "🟡", "🟢"] = "🟢"
    related_questions: list[str] = []


class FrequencyTable(BaseModel):
    course_name: str = ""
    total_exam_years: int = 0
    topics: list[TopicFrequency] = []
    generated_at: datetime = Field(default_factory=datetime.now)


class ExamStrategy(BaseModel):
    questions: list[dict] = []
    best_combination: str = ""
    expected_total: str = ""
    skip_recommendation: str = ""
    generated_at: datetime = Field(default_factory=datetime.now)


class GenerateFrequencyRequest(BaseModel):
    course_name: str = ""


class GenerateStrategyRequest(BaseModel):
    course_name: str = ""
