from celery import Celery
import os


celery_app = Celery(
    "documind",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    task_queues={
        "documents": {},   # procesar documentos subidos
        "agents": {},      # ejecutar agentes AI
    }
)