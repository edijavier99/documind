from app.models.document import DocumentType
from app.core.logging import get_logger

logger = get_logger(__name__)

# Keywords por tipo de documento
# En el Punto 10 entrenamos un modelo real con scikit-learn
DOCUMENT_KEYWORDS = {
    DocumentType.CONTRACT: [
        "agreement", "contract", "parties", "obligations",
        "terms and conditions", "clause", "whereas", "hereinafter",
        "contrato", "acuerdo", "cláusula", "partes",
    ],
    DocumentType.INVOICE: [
        "invoice", "payment", "amount due", "billing",
        "total", "vat", "tax", "factura", "importe", "pago",
    ],
    DocumentType.REPORT: [
        "report", "analysis", "findings", "summary",
        "conclusion", "executive summary", "informe", "análisis",
    ],
    DocumentType.TECHNICAL: [
        "api", "function", "implementation", "architecture",
        "database", "system", "technical", "specification",
        "readme", "documentation",
    ],
}


def classify_document(text: str) -> DocumentType:
    """
    Clasifica un documento basándose en keywords.
    Devuelve el tipo con más coincidencias.
    """
    text_lower = text.lower()
    scores = {}

    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[doc_type] = score

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # Si no hay suficientes coincidencias → unknown
    if best_score < 2:
        return DocumentType.UNKNOWN

    logger.info("document classified", type=best_type, score=best_score)
    return best_type
