"""app/workers/celery_app.py
Configuración del orquestador asíncrono (Celery) con soporte para Dead Letter Queue (ME-02).
"""
import os
import logging
from celery import Celery
from kombu import Exchange, Queue

logger = logging.getLogger("ms_reports.celery")

def create_celery():
    base_redis_url = os.getenv("MS3_REDIS_URL", "redis://reports_redis:6379/0")
    
    broker = os.getenv("MS3_CELERY_BROKER_URL", base_redis_url)
    backend = os.getenv("MS3_CELERY_RESULT_BACKEND", base_redis_url)
    
    celery = Celery("ms3_reports", broker=broker, backend=backend)

    # Definimos los Intercambios (Exchanges)
    default_exchange = Exchange('reports_exchange', type='direct')
    dead_letter_exchange = Exchange('dlq_exchange', type='direct')

    # Definimos las Colas
    celery.conf.task_queues = (
        # Cola Principal
        Queue('reports_queue', default_exchange, routing_key='reports.main'),
        # Cola de Mensajes Muertos (Cuarentena)
        Queue('reports_dlq', dead_letter_exchange, routing_key='reports.dead'),
    )

    # Configuración de Ruteo por Defecto
    celery.conf.task_default_queue = 'reports_queue'
    celery.conf.task_default_exchange = 'reports_exchange'
    celery.conf.task_default_routing_key = 'reports.main'

    # Configuración de Dead Letter Queue (DLQ)
    celery.conf.task_acks_late = True
    celery.conf.task_reject_on_worker_lost = True
    celery.conf.worker_prefetch_multiplier = 1
    celery.conf.task_soft_time_limit = int(os.getenv("MS3_TASK_SOFT_TIME_LIMIT", "600"))

    return celery

celery_app = create_celery()

# Importar tareas
try:
    import app.workers.tasks  # noqa: F401
except Exception as e:
    logger.error(f"Error cargando tareas de Celery: {e}")