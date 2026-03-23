# from app.worker.celery_app import celery_app
# @celery_app.task(queue="documents")
# def process_document(document_id: str):
#     # Lo implementamos en el Punto 7
#     print(f"Processing document: {document_id}")
#     return {"status": "ok"}


# @celery_app.task(queue="agents")
# def run_agent(agent_type: str, document_id: str):
#     # Lo implementamos en el Punto 11
#     print(f"Running agent {agent_type} on {document_id}")
#     return {"status": "ok"}



from app.worker.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    queue="documents",
    bind=True,              # acceso a self para reintentos
    max_retries=3,
    default_retry_delay=60, # espera 60s antes de reintentar
)
def process_document(self, document_id: str):
    """
    Tarea principal de procesamiento de un documento.

    Pasos:
    1. Descarga el archivo de S3
    2. Extrae el texto
    3. Clasifica el tipo de documento
    4. Crea los chunks
    5. Genera embeddings
    6. Guarda chunks+embeddings en PostgreSQL
    7. Actualiza el status del documento
    """
    from app.core.database import SessionLocal
    from app.models.document import Document, DocumentStatus
    from app.models.chunk import Chunk
    from app.services.storage_service import download_file
    from app.services.document_processor import extract_text, chunk_text
    from app.ml.classifier import classify_document
    from app.ml.embeddings import generate_embeddings
    from app.core.config import settings
    import uuid

    db = SessionLocal()

    try:
        # ── 1. Obtener el documento de la DB ──────────────────────
        document = db.query(Document).filter(
            Document.id == uuid.UUID(document_id)
        ).first()

        if not document:
            logger.error("document not found", doc_id=document_id)
            return

        # Actualiza status → processing
        document.status = DocumentStatus.PROCESSING
        db.commit()

        logger.info("processing started", doc_id=document_id, filename=document.filename)

        # ── 2. Descarga de S3 ─────────────────────────────────────
        file_content = download_file(document.s3_key)
        logger.info("file downloaded", doc_id=document_id, size=len(file_content))

        # ── 3. Extrae texto ───────────────────────────────────────
        text, page_count = extract_text(file_content, document.mime_type)

        if not text.strip():
            raise ValueError("No text could be extracted from document")

        document.page_count = page_count
        db.commit()

        # ── 4. Clasifica el documento ─────────────────────────────
        doc_type = classify_document(text)
        document.doc_type = doc_type
        db.commit()

        # ── 5. Chunking ───────────────────────────────────────────
        chunks_data = chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        if not chunks_data:
            raise ValueError("No chunks generated from document")

        # ── 6. Genera embeddings ──────────────────────────────────
        texts = [c["content"] for c in chunks_data]
        embeddings = generate_embeddings(texts)

        # ── 7. Guarda chunks en PostgreSQL ────────────────────────
        # Elimina chunks anteriores si los hay (por si es un reprocesado)
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()

        chunk_objects = []
        for chunk_data, embedding in zip(chunks_data, embeddings):
            chunk = Chunk(
                document_id=document.id,
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                embedding=embedding,
                metadata_=chunk_data["metadata"],
            )
            chunk_objects.append(chunk)

        db.bulk_save_objects(chunk_objects)

        # ── 8. Marca como listo ───────────────────────────────────
        document.status = DocumentStatus.READY
        db.commit()

        logger.info(
            "processing completed",
            doc_id=document_id,
            chunks=len(chunk_objects),
            pages=page_count,
            doc_type=str(doc_type),
        )

        return {
            "status": "completed",
            "document_id": document_id,
            "chunks": len(chunk_objects),
            "pages": page_count,
        }

    except Exception as exc:
        # Marca el documento como fallido
        try:
            document.status = DocumentStatus.FAILED
            db.commit()
        except Exception:
            pass

        logger.error(
            "processing failed",
            doc_id=document_id,
            error=str(exc),
        )

        # Reintenta la tarea si no hemos llegado al máximo
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(queue="agents")
def run_agent(agent_type: str, document_id: str):
    """Lo implementamos en el Punto 11"""
    logger.info("agent task received", agent=agent_type, doc_id=document_id)
    return {"status": "pending_implementation"}
