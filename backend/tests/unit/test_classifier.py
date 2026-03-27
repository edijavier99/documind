from app.ml.classifier import train_classifier, classify_document, get_classification_details
from app.models.document import DocumentType


def test_train_classifier():
    """El modelo entrena sin errores"""
    pipeline = train_classifier(save=False)
    assert pipeline is not None


def test_classify_contract():
    train_classifier(save=False)
    text = """
    This service agreement is entered into between the parties.
    Terms and conditions set forth obligations. This contract
    shall be governed by applicable law. Both parties agree
    to the clauses herein.
    """
    result = classify_document(text)
    assert result == DocumentType.CONTRACT


def test_classify_invoice():
    train_classifier(save=False)
    text = """
    Invoice #2024-123. Bill to: Client Corp.
    Amount due: $5,000. VAT 20% included.
    Payment due within 30 days. Total: $6,000.
    """
    result = classify_document(text)
    assert result == DocumentType.INVOICE


def test_classify_technical():
    train_classifier(save=False)
    text = """
    API documentation for REST endpoints.
    Authentication using JWT tokens. Database PostgreSQL.
    Deploy with Docker and Kubernetes. README installation guide.
    """
    result = classify_document(text)
    assert result == DocumentType.TECHNICAL


def test_classification_details():
    train_classifier(save=False)
    text = "Annual report executive summary findings and analysis conclusions."
    details = get_classification_details(text)

    assert "predicted" in details
    assert "confidence" in details
    assert "probabilities" in details
    assert len(details["probabilities"]) == 4


def test_short_text_returns_unknown():
    result = classify_document("too short")
    assert result == DocumentType.UNKNOWN
