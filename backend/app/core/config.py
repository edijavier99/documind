from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    # ================================
    # App
    # ================================
    APP_ENV: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str
    PROJECT_NAME: str = "DocuMind"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # ================================
    # Base de datos
    # ================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ================================
    # Redis
    # ================================
    REDIS_URL: str = "redis://redis:6379/0"

    # ================================
    # OpenAI
    # ================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ================================
    # Storage (S3 / MinIO)
    # ================================
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "eu-west-1"
    S3_BUCKET_NAME: str
    MINIO_ENDPOINT: str | None = None  # None en producción (usa AWS real)

    # ================================
    # Auth
    # ================================
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24      # 24 horas
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # ================================
    # RAG
    # ================================
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_RETRIEVAL_DOCS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


# lru_cache → el objeto Settings se crea una sola vez (singleton)
# en vez de leer el .env en cada request
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Instancia global — importa esto en cualquier parte del proyecto
settings = get_settings()
