from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid
from app.models.base import TimeStampedModel


class Chunk(TimeStampedModel):
    __tablename__ = "chunks"

    # Contenido
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # El vector de embedding — 1536 dimensiones es el tamaño
    # de text-embedding-3-small de OpenAI
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=True,  # nullable hasta que se procese
    )

    # Metadata del chunk (página, posición, etc.)
    metadata_: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        name="metadata",
    )

    # Relación con el documento
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    def __repr__(self):
        return f"<Chunk {self.chunk_index} of doc {self.document_id}>"
