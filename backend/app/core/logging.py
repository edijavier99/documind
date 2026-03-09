import logging
import sys
import structlog
from app.core.config import settings


def setup_logging() -> None:
    """
    Configura logging estructurado.
    - En development: logs bonitos y coloreados para leer en terminal
    - En production: logs en JSON para CloudWatch
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.APP_ENV == "development":
        # Logs legibles en terminal durante desarrollo
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # JSON para producción → CloudWatch puede parsearlos
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

    # También configura el logging estándar de Python
    # para que librerías como SQLAlchemy usen el mismo sistema
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if settings.APP_ENV != "development" else logging.DEBUG,
    )


def get_logger(name: str):
    """
    Uso:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("documento procesado", doc_id="123", chunks=45)
    """
    return structlog.get_logger(name)
