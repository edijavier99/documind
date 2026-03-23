from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are DocuMind, an AI assistant specialized in analyzing documents.

Your job is to answer questions based EXCLUSIVELY on the provided document context.

Rules:
- Only use information from the provided context
- If the answer is not in the context, say "I couldn't find that information in this document"
- Always cite which source (Source 1, Source 2, etc.) your answer comes from
- Be concise and precise
- If asked in Spanish, answer in Spanish. Match the user's language.
"""


def build_prompt(query: str, context: str) -> list[dict]:
    """
    Construye los mensajes para la API de OpenAI.
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Document context:

{context}

---

Question: {query}

Answer based only on the context above:"""
        }
    ]


def generate_response(query: str, context: str) -> str:
    """
    Genera una respuesta usando el LLM.
    Versión no-streaming — para el Punto 9 añadimos streaming.
    """
    messages = build_prompt(query, context)

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.1,    # baja temperatura = respuestas más precisas y consistentes
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    logger.info(
        "llm response generated",
        query=query[:50],
        tokens_used=response.usage.total_tokens,
    )

    return answer


def generate_response_stream(query: str, context: str):
    """
    Genera respuesta en streaming.
    Devuelve un generador que yields tokens uno a uno.
    Lo usamos en el Punto 9.
    """
    messages = build_prompt(query, context)

    stream = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1000,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
