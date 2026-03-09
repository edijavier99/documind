from sqlalchemy import ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from app.models.base import TimeStampedModel


class InsightType(str, enum.Enum):
    EXTRACTION  = "extraction"   # entidades extraídas
    COMPARISON  = "comparison"   # comparación entre docs
    MONITORING  = "monitoring"   # alertas detectadas


class InsightStatus(str, enum.Enum):
    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETED  = "completed"
    FAILED     = "failed"


class Insight(TimeStampedModel):
    __tablename__ = "insights"

    insight_type: Mapped[InsightType] = mapped_column(
        SAEnum(InsightType),
        nullable=False,
    )
    status: Mapped[InsightStatus] = mapped_column(
        SAEnum(InsightStatus),
        default=InsightStatus.PENDING,
        nullable=False,
    )

    # El resultado del agente — estructura flexible según el tipo
    result: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Si falló, el error
    error: Mapped[str | None] = mapped_column(JSONB, nullable=True)

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="insights",
    )
