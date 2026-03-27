from sqlalchemy.orm import Session
import uuid
from typing import Generator
import json
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.rag_service import (
    hybrid_search,
    rerank_chunks,
    build_context,
    get_document_for_chat,
)
from app.services.llm_service import generate_response,generate_response_stream
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_or_create_session(
    document_id: str,
    user_id: str,
    db: Session,
) -> ChatSession:
    """
    Obtiene la sesión de chat activa para un documento,
    o crea una nueva si no existe.
    Un usuario puede tener una sesión por documento.
    """
    session = db.query(ChatSession).filter(
        ChatSession.document_id == uuid.UUID(document_id),
        ChatSession.user_id == uuid.UUID(user_id),
    ).first()

    if not session:
        session = ChatSession(
            document_id=uuid.UUID(document_id),
            user_id=uuid.UUID(user_id),
            title="New Chat",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info("chat session created", session_id=str(session.id))

    return session


def get_chat_history(session_id: str, db: Session) -> list[ChatMessage]:
    """Obtiene el historial de mensajes de una sesión"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == uuid.UUID(session_id),
    ).order_by(ChatMessage.created_at).all()


def ask_document(
    query: str,
    document_id: str,
    user_id: str,
    db: Session,
) -> dict:
    """
    Pipeline RAG completo:
    1. Verifica el documento
    2. Busca chunks relevantes
    3. Genera respuesta con el LLM
    4. Guarda el intercambio en la DB
    5. Devuelve respuesta + fuentes
    """
    # ── 1. Verifica documento ─────────────────────────────────────
    get_document_for_chat(document_id, user_id, db)

    # ── 2. Hybrid search ──────────────────────────────────────────
    chunks = hybrid_search(
        query=query,
        document_id=document_id,
        db=db,
        top_k=10,
    )

    if not chunks:
        return {
            "answer": "I couldn't find relevant information in this document to answer your question.",
            "sources": [],
        }

    # ── 3. Reranking ──────────────────────────────────────────────
    reranked_chunks = rerank_chunks(query, chunks)

    # ── 4. Construye contexto ─────────────────────────────────────
    context, sources = build_context(reranked_chunks[:5])

    # ── 5. Genera respuesta ───────────────────────────────────────
    answer = generate_response(query, context)

    # ── 6. Guarda en DB ───────────────────────────────────────────
    session = get_or_create_session(document_id, user_id, db)

    # Guarda la pregunta del usuario
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=query,
        sources=[],
    )
    db.add(user_message)

    # Guarda la respuesta del asistente con las fuentes
    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=answer,
        sources=sources,
    )
    db.add(assistant_message)
    db.commit()

    logger.info(
        "chat response saved",
        doc_id=document_id,
        session_id=str(session.id),
        sources=len(sources),
    )

    return {
        "answer": answer,
        "sources": sources,
        "session_id": str(session.id),
    }



def ask_document_stream(
    query: str,
    document_id: str,
    user_id: str,
    db: Session,
) -> Generator[str, None, None]:
    """
    Versión streaming del pipeline RAG.

    Yields eventos SSE con este formato:
        data: {"type": "sources", "data": [...]}
        data: {"type": "token", "data": "Hola"}
        data: {"type": "token", "data": " mundo"}
        data: {"type": "done", "data": ""}

    El frontend escucha estos eventos y los va pintando.
    """
    # ── 1. RAG: busca chunks relevantes ──────────────────────────
    get_document_for_chat(document_id, user_id, db)

    chunks = hybrid_search(query=query, document_id=document_id, db=db, top_k=10)

    if not chunks:
        yield _sse_event("error", "I couldn't find relevant information in this document.")
        return

    reranked = rerank_chunks(query, chunks)
    context, sources = build_context(reranked[:5])

    # ── 2. Manda las fuentes primero ──────────────────────────────
    # El frontend puede mostrar las fuentes mientras el LLM responde
    yield _sse_event("sources", sources)

    # ── 3. Stream de tokens del LLM ───────────────────────────────
    full_answer = ""

    for token in generate_response_stream(query, context):
        full_answer += token
        yield _sse_event("token", token)

    # ── 4. Guarda en DB cuando termina el stream ──────────────────
    session = get_or_create_session(document_id, user_id, db)

    db.add(ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=query,
        sources=[],
    ))
    db.add(ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=full_answer,
        sources=sources,
    ))
    db.commit()

    # ── 5. Señal de fin del stream ────────────────────────────────
    yield _sse_event("done", {"session_id": str(session.id)})


def _sse_event(event_type: str, data) -> str:
    """
    Formatea un evento SSE.

    El formato SSE es:
        data: {json}\n\n

    El doble salto de línea indica el fin del evento.
    """
    payload = json.dumps({"type": event_type, "data": data})
    return f"data: {payload}\n\n"