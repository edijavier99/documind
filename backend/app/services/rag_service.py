from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus
from app.ml.embeddings import generate_single_embedding
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def semantic_search(
    query: str,
    document_id: str,
    db: Session,
    top_k: int = 20,
) -> list[Chunk]:
    """
    Búsqueda semántica pura usando pgvector.
    Devuelve los top_k chunks más similares al query.

    El operador <=> es la distancia coseno en pgvector.
    Menor distancia = más similar.
    """
    query_embedding = generate_single_embedding(query)

    # Convierte el vector a string que entiende pgvector
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    results = db.execute(
        text("""
            SELECT id, content, chunk_index, metadata,
                   1 - (embedding <=> vector(:embedding)) as similarity
            FROM chunks
            WHERE document_id = :document_id
            ORDER BY embedding <=> vector(:embedding)
            LIMIT :top_k
        """),
        {
            "embedding": embedding_str,
            "document_id": document_id,
            "top_k": top_k,
        }
    ).fetchall()

    logger.info(
        "semantic search",
        query=query[:50],
        results=len(results),
        top_similarity=round(results[0].similarity, 3) if results else 0,
    )

    return results


def keyword_search(
    query: str,
    document_id: str,
    db: Session,
    top_k: int = 20,
) -> list:
    """
    Búsqueda por keywords usando full-text search de PostgreSQL.
    Complementa la búsqueda semántica — buena para términos exactos,
    nombres propios, números, fechas.
    """
    results = db.execute(
        text("""
            SELECT id, content, chunk_index, metadata,
                   ts_rank(
                       to_tsvector('english', content),
                       plainto_tsquery('english', :query)
                   ) as rank
            FROM chunks
            WHERE document_id = :document_id
              AND to_tsvector('english', content) @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :top_k
        """),
        {
            "query": query,
            "document_id": document_id,
            "top_k": top_k,
        }
    ).fetchall()

    logger.info("keyword search", query=query[:50], results=len(results))
    return results


def hybrid_search(
    query: str,
    document_id: str,
    db: Session,
    top_k: int = 10,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> list[dict]:
    """
    Hybrid search = semántico + keywords combinados.

    Por qué es mejor que solo semántico:
    - Semántico: entiende el significado, falla con términos exactos
    - Keywords: exacto, falla con sinónimos o paráfrasis
    - Híbrido: lo mejor de los dos

    Ejemplo:
    Query: "¿Cuánto es el pago mensual?"
    - Semántico encuentra: chunks sobre "fee", "cost", "pricing"
    - Keywords encuentra: chunks con "pago" exacto
    - Híbrido combina ambos con pesos
    """
    semantic_results = semantic_search(query, document_id, db, top_k=20)
    keyword_results = keyword_search(query, document_id, db, top_k=20)

    # Combina resultados usando Reciprocal Rank Fusion (RRF)
    # Técnica estándar para combinar rankings de diferentes sistemas
    scores = {}

    for rank, result in enumerate(semantic_results):
        chunk_id = str(result.id)
        if chunk_id not in scores:
            scores[chunk_id] = {"result": result, "score": 0}
        # RRF: 1 / (rank + 60) — penaliza posiciones bajas
        scores[chunk_id]["score"] += semantic_weight * (1 / (rank + 60))

    for rank, result in enumerate(keyword_results):
        chunk_id = str(result.id)
        if chunk_id not in scores:
            scores[chunk_id] = {"result": result, "score": 0}
        scores[chunk_id]["score"] += keyword_weight * (1 / (rank + 60))

    # Ordena por score combinado y devuelve top_k
    sorted_chunks = sorted(
        scores.values(),
        key=lambda x: x["score"],
        reverse=True,
    )[:top_k]

    logger.info(
        "hybrid search completed",
        semantic=len(semantic_results),
        keyword=len(keyword_results),
        combined=len(sorted_chunks),
    )

    return [item["result"] for item in sorted_chunks]


def rerank_chunks(query: str, chunks: list) -> list:
    """
    Reranking — segunda pasada de relevancia.

    Después del hybrid search tenemos los top 10 chunks.
    El reranking los reordena con un criterio más fino:
    evalúa cuánto responde cada chunk directamente a la pregunta.

    Implementación simple basada en overlap de términos.
    En producción usarías un modelo cross-encoder (ej: Cohere Rerank).
    """
    query_terms = set(query.lower().split())

    def relevance_score(chunk) -> float:
        content_lower = chunk.content.lower()
        # Cuenta cuántos términos del query aparecen en el chunk
        term_overlap = sum(1 for term in query_terms if term in content_lower)
        # Normaliza por longitud del query
        return term_overlap / max(len(query_terms), 1)

    return sorted(chunks, key=relevance_score, reverse=True)


def build_context(chunks: list, max_tokens: int = 3000) -> tuple[str, list[dict]]:
    """
    Construye el bloque de contexto que va en el prompt.

    - Respeta el límite de tokens para no exceder el contexto del LLM
    - Devuelve también las fuentes para citarlas en la respuesta
    """
    context_parts = []
    sources = []
    total_chars = 0
    # Estimación simple: 1 token ≈ 4 caracteres
    max_chars = max_tokens * 4

    for i, chunk in enumerate(chunks):
        chunk_text = chunk.content
        if total_chars + len(chunk_text) > max_chars:
            break

        context_parts.append(f"[Source {i + 1}]\n{chunk_text}")
        sources.append({
            "index": i + 1,
            "chunk_index": chunk.chunk_index,
            "preview": chunk_text[:150] + "..." if len(chunk_text) > 150 else chunk_text,
        })
        total_chars += len(chunk_text)

    context = "\n\n---\n\n".join(context_parts)
    return context, sources


def get_document_for_chat(
    document_id: str,
    user_id: str,
    db: Session,
) -> Document:
    """
    Verifica que el documento existe, pertenece al usuario y está listo.
    """
    document = db.query(Document).filter(
        Document.id == uuid.UUID(document_id),
        Document.owner_id == uuid.UUID(user_id),
    ).first()

    if not document:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status != DocumentStatus.READY:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document is not ready yet. Current status: {document.status}",
        )

    return document
