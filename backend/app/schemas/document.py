from pydantic import BaseModel
from datetime import datetime
from app.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    doc_type: DocumentType
    file_size: int | None
    page_count: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
