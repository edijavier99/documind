from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Genera embeddings para una lista de textos.
    Los manda en batch para minimizar llamadas a la API.

    Devuelve lista de vectores (1536 dimensiones cada uno).
    """
    if not texts:
        return []

    # OpenAI acepta hasta 2048 inputs por llamada
    # Procesamos en batches de 100 para ser conservadores
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Limpia los textos — OpenAI no acepta strings vacíos
        batch = [t.strip() or " " for t in batch]

        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=batch,
        )

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

        logger.info(
            "embeddings generated",
            batch=i // batch_size + 1,
            count=len(batch),
        )

    return all_embeddings


def generate_single_embedding(text: str) -> list[float]:
    """Genera embedding para un solo texto (usado en queries del chat)"""
    embeddings = generate_embeddings([text])
    return embeddings[0] if embeddings else []
