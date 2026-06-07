"""app/infrastructure/monitoring/metrics.py

Definición de métricas de Prometheus para observabilidad del sistema.
Mide rendimiento HTTP, tasas de error y monitorea la salud de la cola asíncrona.
"""
import time
import redis
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

from app.core.config import settings

logger = logging.getLogger("ms_reports.metrics")

# ============================================================================
# DEFINICIÓN DE MÉTRICAS (PROMETHEUS REGISTRY)
# ============================================================================

# 1. Peticiones HTTP
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de peticiones HTTP recibidas",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duración de las peticiones HTTP en segundos",
    ["method", "endpoint"]
)

# 2. Errores de Negocio
REPORT_GENERATION_ERRORS = Counter(
    "report_generation_errors_total",
    "Total de errores críticos en la generación de PDFs",
    ["error_type"]
)

# 3. Salud de la Infraestructura (Celery)
CELERY_QUEUE_LENGTH = Gauge(
    "celery_queue_length",
    "Número de tareas pendientes de procesamiento en la cola de Celery"
)

# ============================================================================
# RECOLECTOR DINÁMICO
# ============================================================================

def get_metrics_response() -> Response:
    """
    Calcula métricas dinámicas en tiempo real (como la cola de Redis) 
    y formatea el registro completo para que Prometheus lo consuma (Scrape).
    """
    try:
        # Nos conectamos a Redis para ver cuántos jobs de Celery están pendientes
        r = redis.from_url(settings.REDIS_URL)
        queue_length = r.llen("reports_queue")
        CELERY_QUEUE_LENGTH.set(queue_length)
    except Exception as e:
        logger.error(f"Error al leer la cola de Celery desde Redis: {e}")
        CELERY_QUEUE_LENGTH.set(0)

    # Retornamos las métricas en formato texto (estándar de Prometheus)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)