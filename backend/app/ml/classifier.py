from app.models.document import DocumentType
from app.core.logging import get_logger
import os
import pickle
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder


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


# def classify_document(text: str) -> DocumentType:
#     """
#     Clasifica un documento basándose en keywords.
#     Devuelve el tipo con más coincidencias.
#     """
#     text_lower = text.lower()
#     scores = {}

#     for doc_type, keywords in DOCUMENT_KEYWORDS.items():
#         score = sum(1 for kw in keywords if kw in text_lower)
#         scores[doc_type] = score

#     best_type = max(scores, key=scores.get)
#     best_score = scores[best_type]

#     # Si no hay suficientes coincidencias → unknown
#     if best_score < 2:
#         return DocumentType.UNKNOWN

#     logger.info("document classified", type=best_type, score=best_score)
#     return best_type






# Ruta donde se guarda el modelo entrenado
MODEL_PATH = "/app/app/ml/document_classifier.pkl"


def build_pipeline() -> Pipeline:
    """
    Construye el pipeline de ML:

    TF-IDF → LinearSVC

    TF-IDF convierte texto a vectores numéricos.
    LinearSVC es rápido, funciona bien con texto, y
    generaliza bien con pocos datos de entrenamiento.

    CalibratedClassifierCV añade probabilidades al SVC
    (por defecto LinearSVC no las tiene).
    """
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=10000,     # top 10k palabras más relevantes
            ngram_range=(1, 2),     # unigramas y bigramas
            min_df=1,               # mínimo 1 documento
            max_df=0.95,            # ignora palabras en >95% de docs
            sublinear_tf=True,      # aplica log a TF (mejora rendimiento)
            strip_accents="unicode",
            analyzer="word",
        )),
        ("classifier", CalibratedClassifierCV(
            LinearSVC(
                C=1.0,              # parámetro de regularización
                max_iter=2000,
            )
        )),
    ])


def train_classifier(save: bool = True) -> Pipeline:
    """
    Entrena el clasificador con los datos de entrenamiento.
    Guarda el modelo en disco para reutilizarlo.
    """
    from app.ml.training_data import TRAINING_DATA

    texts = [text for text, label in TRAINING_DATA]
    labels = [label for text, label in TRAINING_DATA]

    pipeline = build_pipeline()

    # Cross-validation para estimar accuracy real
    scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    logger.info(
        "cross validation complete",
        mean_accuracy=round(scores.mean(), 3),
        std=round(scores.std(), 3),
    )

    # Entrena con todos los datos
    pipeline.fit(texts, labels)

    if save:
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(pipeline, f)
        logger.info("model saved", path=MODEL_PATH)

    return pipeline


def load_classifier() -> Pipeline:
    """
    Carga el modelo desde disco.
    Si no existe, lo entrena primero.
    """
    if not os.path.exists(MODEL_PATH):
        logger.info("model not found, training now")
        return train_classifier()

    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)

    logger.info("model loaded", path=MODEL_PATH)
    return pipeline


# Singleton — el modelo se carga una vez en memoria
_classifier = None


def get_classifier() -> Pipeline:
    """Devuelve el clasificador, cargándolo si es necesario"""
    global _classifier
    if _classifier is None:
        _classifier = load_classifier()
    return _classifier


def classify_document(text: str) -> DocumentType:
    """
    Clasifica un documento usando el modelo ML.

    Devuelve el DocumentType más probable.
    Si la confianza es baja → UNKNOWN.
    """
    if not text or len(text.strip()) < 50:
        return DocumentType.UNKNOWN

    classifier = get_classifier()

    # Trunca el texto — los primeros 3000 chars suelen ser suficientes
    # y evita problemas con documentos muy largos
    text_sample = text[:3000]

    # Predicción con probabilidades
    probabilities = classifier.predict_proba([text_sample])[0]
    classes = classifier.classes_
    predicted_label = classes[np.argmax(probabilities)]
    confidence = np.max(probabilities)

    logger.info(
        "document classified",
        predicted=predicted_label,
        confidence=round(float(confidence), 3),
    )

    # Si la confianza es menor al 40% → no sabemos
    if confidence < 0.40:
        return DocumentType.UNKNOWN

    # Mapea el label string al enum
    type_map = {
        "contract": DocumentType.CONTRACT,
        "invoice": DocumentType.INVOICE,
        "report": DocumentType.REPORT,
        "technical": DocumentType.TECHNICAL,
    }

    return type_map.get(predicted_label, DocumentType.UNKNOWN)


def get_classification_details(text: str) -> dict:
    """
    Versión detallada — devuelve probabilidades para todos los tipos.
    Útil para el frontend y para debugging.
    """
    if not text or len(text.strip()) < 50:
        return {"predicted": "unknown", "confidence": 0.0, "probabilities": {}}

    classifier = get_classifier()
    text_sample = text[:3000]

    probabilities = classifier.predict_proba([text_sample])[0]
    classes = classifier.classes_

    probs_dict = {
        label: round(float(prob), 3)
        for label, prob in zip(classes, probabilities)
    }

    predicted = classes[np.argmax(probabilities)]
    confidence = float(np.max(probabilities))

    return {
        "predicted": predicted,
        "confidence": round(confidence, 3),
        "probabilities": probs_dict,
    }
