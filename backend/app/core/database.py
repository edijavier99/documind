from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Motor de conexión a PostgreSQL
# pool_pre_ping → verifica que la conexión sigue viva antes de usarla
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,           # conexiones simultáneas en el pool
    max_overflow=20,        # conexiones extra si el pool está lleno
    echo=settings.APP_ENV == "development",  # loguea SQL en dev
)

# Fábrica de sesiones — cada request obtiene su propia sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Clase base de la que heredan todos los modelos
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency de FastAPI — inyecta una sesión de DB en cada endpoint.
    Garantiza que la sesión se cierra aunque haya un error.

    Uso en un endpoint:
        def mi_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Activa la extensión pgvector en PostgreSQL.
    Se llama una vez al arrancar la app.
    """
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        logger.info("pgvector extension ready")
