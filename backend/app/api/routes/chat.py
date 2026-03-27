from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.chat_service import ask_document, get_or_create_session, get_chat_history, ask_document_stream

router = APIRouter()



@router.post("/{doc_id}/stream")
def chat_stream(
    doc_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat con streaming — los tokens llegan uno a uno.

    Devuelve un Server-Sent Events stream.
    El frontend lo consume con EventSource o fetch + ReadableStream.

    Eventos que emite:
    - sources: los chunks usados como contexto
    - token:   cada token de la respuesta
    - done:    fin del stream con session_id
    - error:   si algo falla
    """
    return StreamingResponse(
        ask_document_stream(
            query=request.query,
            document_id=doc_id,
            user_id=str(current_user.id),
            db=db,
        ),
        media_type="text/event-stream",
        headers={
            # Estos headers evitan que proxies y browsers buffereen el stream
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )



@router.post("/{doc_id}", response_model=ChatResponse)
def chat_with_document(
    doc_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Hace una pregunta sobre un documento.

    El pipeline RAG:
    1. Busca chunks relevantes (hybrid search)
    2. Reordena por relevancia (reranking)
    3. Genera respuesta con el LLM
    4. Devuelve respuesta + fuentes citadas
    """
    result = ask_document(
        query=request.query,
        document_id=doc_id,
        user_id=str(current_user.id),
        db=db,
    )
    return result


@router.get("/{doc_id}/history", response_model=ChatHistoryResponse)
def get_history(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve el historial de chat de un documento.
    """
    session = get_or_create_session(doc_id, str(current_user.id), db)
    messages = get_chat_history(str(session.id), db)

    return ChatHistoryResponse(
        session_id=str(session.id),
        messages=messages,
    )
