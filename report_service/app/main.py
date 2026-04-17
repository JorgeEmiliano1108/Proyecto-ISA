"""app/main.py
Punto de entrada principal para el microservicio de Reportes y Analítica.
Implementa Arquitectura Hexagonal, CORS, Rate Limiting, Observabilidad y Secure Error Handling.
"""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# --- Importaciones de Rate Limiting ---
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# --- Importaciones de Manejo de Errores (OWASP DS-04) ---
from app.core.exceptions import AppException, app_exception_handler

# --- Importaciones de Métricas (Prometheus) ---
from app.infrastructure.monitoring.metrics import (
    get_metrics_response, 
    HTTP_REQUESTS_TOTAL, 
    HTTP_REQUEST_DURATION_SECONDS
)

# --- Importaciones de Trazabilidad (OpenTelemetry - HI-04) ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from app.infrastructure.api.routers import router as api_router, limiter
from app.core.config import settings

logger = logging.getLogger("ms_reports.main")

# ============================================================================
# CONFIGURACIÓN DE OPENTELEMETRY (Lado Productor)
# ============================================================================
# En producción, aquí agregarías un exportador (ej. JaegerExporter o OTLPSpanExporter)
trace.set_tracer_provider(TracerProvider())

# Instrumentamos Celery ANTES de mandar tareas, para que inyecte el trace_id en Redis
CeleryInstrumentor().instrument()

# --- MANEJO DE CICLO DE VIDA ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando MS-Reports (ISA Corporativo)...")
    yield
    logger.info("Apagando MS-Reports...")

app = FastAPI(
    title="ISA Reports & Analytics Service", 
    version="1.0.0",
    description="Microservicio de generación de reportes PDF inmutables con IA.",
    lifespan=lifespan
)

# Instrumentamos FastAPI para que cada request HTTP genere un Span y un Trace ID
FastAPIInstrumentor.instrument_app(app)

# --- VINCULACIÓN DE MANEJADORES DE EXCEPCIONES Y SEGURIDAD ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Vinculamos nuestro manejador centralizado de errores seguros
app.add_exception_handler(AppException, app_exception_handler)

# --- MIDDLEWARE DE OBSERVABILIDAD (PROMETHEUS) ---
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    start_time = time.time()
    try:
        response = await call_next(request)
        status_code = response.status_code
        if endpoint != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        return response
    except Exception as e:
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=500).inc()
        raise e

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTS DEL SISTEMA (HEALTH & METRICS) ---
@app.get("/health", tags=["System"], summary="Verifica el estado del microservicio")
def health_check():
    return {"status": "ok", "service": "reports_service", "version": "1.0.0"}

@app.get("/metrics", tags=["System"], summary="Expone métricas para Prometheus")
def metrics_endpoint():
    return get_metrics_response()

# --- REGISTRO DE RUTAS DE NEGOCIO ---
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)