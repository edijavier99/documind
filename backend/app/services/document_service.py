from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.services.storage_service import upload_file, delete_file
from app.core.logging import get_logger

logger = get_logger(__name__)

# Tipos de archivo permitidos
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def validate_file(filename: str, content_type: str, file_size: int) -> None:
    """Valida tipo y tamaño del archivo antes de subirlo"""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{content_type}' not supported. Allowed: PDF, DOCX, TXT",
        )
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is 50MB",
        )


def create_document(
    file_content: bytes,
    filename: str,
    content_type: str,
    owner: User,
    db: Session,
) -> Document:
    """
    Sube el archivo a S3 y crea el registro en la DB.
    """
    file_size = len(file_content)
    validate_file(filename, content_type, file_size)

    # Sube a S3/MinIO
    s3_key = upload_file(file_content, filename, content_type)

    # Crea registro en DB
    document = Document(
        filename=filename,
        s3_key=s3_key,
        file_size=file_size,
        mime_type=content_type,
        status=DocumentStatus.PENDING,
        owner_id=owner.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(
        "document created",
        doc_id=str(document.id),
        filename=filename,
        owner=str(owner.id),
    )
    return document


def get_document(doc_id: str, owner: User, db: Session) -> Document:
    """
    Obtiene un documento verificando que pertenece al usuario.
    """
    try:
        doc_uuid = uuid.UUID(doc_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )

    document = db.query(Document).filter(
        Document.id == doc_uuid,
        Document.owner_id == owner.id,
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_id}' not found",
        )
    return document


def list_documents(owner: User, db: Session) -> list[Document]:
    """Lista todos los documentos del usuario ordenados por fecha"""
    return (
        db.query(Document)
        .filter(Document.owner_id == owner.id)
        .order_by(Document.created_at.desc())
        .all()
    )


def delete_document(doc_id: str, owner: User, db: Session) -> None:
    """Elimina documento de S3 y de la DB"""
    document = get_document(doc_id, owner, db)

    # Elimina de S3
    delete_file(document.s3_key)

    # Elimina de DB (cascade elimina chunks, chats, insights)
    db.delete(document)
    db.commit()

    logger.info("document deleted", doc_id=doc_id, owner=str(owner.id))
