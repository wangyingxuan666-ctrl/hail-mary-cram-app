from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    doc_type: Literal["material", "exam"]
    page_count: int = 0


class DocumentResponse(DocumentBase):
    id: str
    chunk_count: int = 0
    content_preview: str = ""
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed: bool = False


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
