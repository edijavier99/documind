import fitz  # PyMuPDF
import docx
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text(file_content: bytes, mime_type: str) -> tuple[str, int]:
    """
    Extrae el texto de un documento.
    Devuelve (texto_completo, numero_de_paginas)
    """
    if mime_type == "application/pdf":
        return _extract_from_pdf(file_content)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _extract_from_docx(file_content)
    elif mime_type == "text/plain":
        return file_content.decode("utf-8", errors="ignore"), 1
    else:
        raise ValueError(f"Unsupported mime type: {mime_type}")


def _extract_from_pdf(file_content: bytes) -> tuple[str, int]:
    """Extrae texto de un PDF página por página"""
    doc = fitz.open(stream=file_content, filetype="pdf")
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():  # ignora páginas vacías
            pages.append(f"[Page {page_num + 1}]\n{text}")

    full_text = "\n\n".join(pages)
    page_count = len(doc)
    doc.close()

    logger.info("pdf extracted", pages=page_count, chars=len(full_text))
    return full_text, page_count


def _extract_from_docx(file_content: bytes) -> tuple[str, int]:
    """Extrae texto de un archivo Word"""
    import io
    doc = docx.Document(io.BytesIO(file_content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n\n".join(paragraphs)
    return full_text, 1


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Divide el texto en chunks con overlap.

    El overlap evita perder contexto en los bordes:

    Chunk 1: [--------------------]
    Chunk 2:             [--------------------]
                         ^ overlap

    Devuelve lista de dicts con content e index.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size

        # Si no es el último chunk, busca un punto de corte natural
        # (salto de línea o espacio) para no cortar palabras a la mitad
        if end < len(text):
            # Busca el último salto de línea dentro del chunk
            cut = text.rfind("\n", start, end)
            if cut == -1:
                # Si no hay salto de línea, busca el último espacio
                cut = text.rfind(" ", start, end)
            if cut != -1:
                end = cut

        chunk_content = text[start:end].strip()

        if chunk_content:
            chunks.append({
                "content": chunk_content,
                "chunk_index": chunk_index,
                "metadata": {
                    "start_char": start,
                    "end_char": end,
                }
            })
            chunk_index += 1

        # El siguiente chunk empieza con overlap
        start = end - chunk_overlap

    logger.info("text chunked", total_chunks=len(chunks), chunk_size=chunk_size)
    return chunks
