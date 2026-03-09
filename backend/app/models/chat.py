from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from app.models.base import TimeStampedModel


class MessageRole(str, enum.Enum):
    USER      = "user"
    ASSISTANT = "assistant"
    SYSTEM    = "system"


class ChatSession(TimeStampedModel):
    __tablename__ = "chat_sessions"

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        default="New Chat",
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chat_sessions",
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(TimeStampedModel):
    __tablename__ = "chat_messages"

    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Los chunks que se usaron para generar esta respuesta
    sources: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )
