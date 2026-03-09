from sqlalchemy import String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from app.models.base import TimeStampedModel


class DocumentStatus(str, enum.Enum):
    PENDING    = "pending"      # recién subido, en cola
    PROCESSING = "processing"   # Celery lo está procesando
    READY      = "ready"        # indexado, listo para chatear
    FAILED     = "failed"       # algo salió mal


class DocumentType(str, enum.Enum):
    CONTRACT   = "contract"
    INVOICE    = "invoice"
    REPORT     = "report"
    TECHNICAL  = "technical"
    UNKNOWN    = "unknown"


class Document(TimeStampedModel):
    __tablename__ = "documents"

    # Info del archivo
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True)

    # Estado y clasificación
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus),
        default=DocumentStatus.PENDING,
        nullable=False,
        index=True,
    )
    doc_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType),
        default=DocumentType.UNKNOWN,
        nullable=False,
    )

    # Metadata flexible — cualquier cosa extra va aquí
    metadata_: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        name="metadata",
    )

    # Relaciones
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped["User"] = relationship("User", back_populates="documents")

    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    insights: Mapped[list["Insight"]] = relationship(
        "Insight",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Document {self.filename} [{self.status}]>"
