# app/workers/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab

# Obtenemos la URL de Redis desde las variables de entorno
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Inicializamos la aplicación Celery
celery_app = Celery(
    "approval_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"] # Le decimos dónde buscar las tareas
)

# Configuración estricta de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Mexico_City", # Ajustado al horario del corporativo
    enable_utc=True,
    # Evita que un worker consuma toda la memoria si hay miles de tareas
    worker_max_tasks_per_child=100 
)


# Cronjobs (Celery Beat Schedule)
celery_app.conf.beat_schedule = {
    "barrido-diario-evaluaciones-atoradas": {
        "task": "app.workers.tasks.send_pending_reminders",
        # Se ejecuta todos los días a las 08:00 AM
        "schedule": crontab(hour=8, minute=0), 
    },
}