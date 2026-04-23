from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bonus_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Mexico_City",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # Confirma la tarea solo después de completarla
    worker_prefetch_multiplier=1,  # Un mensaje a la vez por worker (CPU-bound)
    result_expires=3600,           # Resultados disponibles 1 hora
)
