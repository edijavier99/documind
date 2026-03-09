import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import uuid
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_s3_client():
    """
    Devuelve un cliente S3.
    - En desarrollo apunta a MinIO (endpoint local)
    - En producción apunta a AWS S3 real
    """
    kwargs = {
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        "region_name": settings.AWS_REGION,
        "config": Config(signature_version="s3v4"),
    }

    # Si hay endpoint configurado → MinIO local
    if settings.MINIO_ENDPOINT:
        kwargs["endpoint_url"] = settings.MINIO_ENDPOINT

    return boto3.client("s3", **kwargs)


def ensure_bucket_exists():
    """
    Crea el bucket si no existe.
    En producción el bucket ya existe (creado por Terraform).
    En desarrollo lo creamos automáticamente.
    """
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        logger.info("bucket exists", bucket=settings.S3_BUCKET_NAME)
    except ClientError:
        client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
        logger.info("bucket created", bucket=settings.S3_BUCKET_NAME)


def upload_file(file_content: bytes, filename: str, content_type: str) -> str:
    """
    Sube un archivo a S3/MinIO.
    Devuelve la s3_key (la ruta dentro del bucket).

    La key tiene formato: documents/{uuid}/{filename}
    El UUID evita colisiones si dos usuarios suben el mismo nombre
    """
    client = get_s3_client()
    file_id = str(uuid.uuid4())
    s3_key = f"documents/{file_id}/{filename}"

    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
        Body=file_content,
        ContentType=content_type,
    )

    logger.info("file uploaded", s3_key=s3_key, size=len(file_content))
    return s3_key


def download_file(s3_key: str) -> bytes:
    """
    Descarga un archivo de S3/MinIO.
    Lo usa el worker de Celery para procesar el documento.
    """
    client = get_s3_client()
    response = client.get_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
    )
    return response["Body"].read()


def delete_file(s3_key: str) -> None:
    """Elimina un archivo de S3/MinIO"""
    client = get_s3_client()
    client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
    logger.info("file deleted", s3_key=s3_key)


def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    """
    Genera una URL temporal para que el frontend
    pueda descargar el archivo directamente desde S3
    sin pasar por el backend.
    Expira en 1 hora por defecto.
    """
    client = get_s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=expires_in,
    )
    return url
