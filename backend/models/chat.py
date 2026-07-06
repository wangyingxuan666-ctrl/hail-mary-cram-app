from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"
    content: str
    question_ref: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_paper: str = ""
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)


class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    question_ref: Optional[str] = None


class StartSessionRequest(BaseModel):
    exam_paper: str = ""


class ExplainTopicRequest(BaseModel):
    topic: str
    include_rag: bool = True
