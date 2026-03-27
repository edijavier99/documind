from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse,
)
from app.services.document_service import (
    create_document,
    get_document,
    list_documents,
    delete_document,
)
from app.services.storage_service import generate_presigned_url

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sube un documento (PDF, DOCX, TXT).
    Máximo 50MB.
    El documento queda en estado 'pending' hasta que
    el worker lo procese.
    """
    file_content = await file.read()


    document = create_document(
        file_content=file_content,
        filename=file.filename,
        content_type=file.content_type,
        owner=current_user,
        db=db,
    )

    # Dispara el procesamiento en background (Celery)
    # Lo activamos en el Punto 7
    from app.worker.tasks import process_document
    process_document.delay(str(document.id))

    return DocumentUploadResponse(
        message="Document uploaded successfully. Processing started.",
        document=document,
    )


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos los documentos del usuario autenticado"""
    documents = list_documents(current_user, db)
    return DocumentListResponse(
        documents=documents,
        total=len(documents),
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document_by_id(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un documento por ID"""
    return get_document(doc_id, current_user, db)


@router.get("/{doc_id}/download-url")
def get_download_url(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Genera una URL temporal (1 hora) para descargar
    el archivo original directamente desde S3.
    """
    document = get_document(doc_id, current_user, db)
    url = generate_presigned_url(document.s3_key)
    return {"download_url": url, "expires_in": 3600}


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un documento y todos sus datos asociados"""
    delete_document(doc_id, current_user, db)




@router.get("/{doc_id}/status")
def get_document_status(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve el status actual del documento.
    El frontend llama a este endpoint cada 3 segundos
    hasta que el status sea 'ready' o 'failed'.
    """
    document = get_document(doc_id, current_user, db)
    return {
        "doc_id": doc_id,
        "status": document.status,
        "doc_type": document.doc_type,
        "page_count": document.page_count,
    }




@router.get("/{doc_id}/classification")
def get_classification(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve la clasificación detallada del documento
    con las probabilidades de cada tipo.
    Útil para debugging y para mostrar en el frontend.
    """
    from app.ml.classifier import get_classification_details
    from app.services.storage_service import download_file
    from app.services.document_processor import extract_text

    document = get_document(doc_id, current_user, db)

    # Descarga y extrae texto para reclasificar
    file_content = download_file(document.s3_key)
    text, _ = extract_text(file_content, document.mime_type)

    details = get_classification_details(text)

    return {
        "doc_id": doc_id,
        "current_type": document.doc_type,
        "classification": details,
    }