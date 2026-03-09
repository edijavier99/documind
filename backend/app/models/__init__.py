# Importar todos los modelos aquí para que Alembic los detecte
from app.models.base import TimeStampedModel
from app.models.user import User
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.chunk import Chunk
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.insight import Insight, InsightType, InsightStatus

__all__ = [
    "TimeStampedModel",
    "User",
    "Document", "DocumentStatus", "DocumentType",
    "Chunk",
    "ChatSession", "ChatMessage", "MessageRole",
    "Insight", "InsightType", "InsightStatus",
]
