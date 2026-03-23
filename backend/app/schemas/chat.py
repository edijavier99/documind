from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ChatRequest(BaseModel):
    query: str
    document_id: str


class SourceReference(BaseModel):
    index: int
    chunk_index: int
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    session_id: str


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: list
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]
