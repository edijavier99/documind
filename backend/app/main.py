from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db
from app.services.storage_service import ensure_bucket_exists


setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration,
        )
        return response

    from app.api.routes import documents, chat, agents, insights, auth
    app.include_router(auth.router,      prefix=f"{settings.API_PREFIX}/auth",      tags=["auth"])
    app.include_router(documents.router, prefix=f"{settings.API_PREFIX}/documents", tags=["documents"])
    app.include_router(chat.router,      prefix=f"{settings.API_PREFIX}/chat",      tags=["chat"])
    app.include_router(agents.router,    prefix=f"{settings.API_PREFIX}/agents",    tags=["agents"])
    app.include_router(insights.router,  prefix=f"{settings.API_PREFIX}/insights",  tags=["insights"])

    @app.on_event("startup")
    async def startup():
        init_db()  # activa pgvector
        ensure_bucket_exists()
        logger.info("starting documind api", env=settings.APP_ENV, version=settings.VERSION)

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("shutting down documind api")

    @app.get("/health", tags=["system"])
    def health_check():
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "env": settings.APP_ENV,
        }

    return app


app = create_app()


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI(
#     title="DocuMind API",
#     description="AI Document Intelligence Platform",
#     version="0.1.0",
# )

# # CORS — permite que el frontend (localhost:3000) hable con la API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/health")
# def health_check():
#     return {
#         "status": "ok",
#         "service": "documind-api",
#         "version": "0.1.0"
#     }
