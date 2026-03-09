from pydantic import BaseModel, computed_field
from datetime import datetime
from app.models.document import DocumentStatus, DocumentType
from datetime import datetime
from app.models.document import DocumentStatus, DocumentType
from uuid import UUID


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: DocumentStatus
    doc_type: DocumentType
    file_size: int | None
    page_count: int | None
    mime_type: str | None
    created_at: datetime

    @computed_field
    @property
    def size_mb(self) -> float | None:
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
