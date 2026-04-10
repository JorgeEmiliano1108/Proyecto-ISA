# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AuditServiceException
from app.domain.exceptions import DomainException
from app.infrastructure.api.routers import router as audit_router
from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Lifespan Events (Arranque y Apagado)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: (Solo para dev local) Crear tablas si no existen.
    # En Producción, DEBES usar Alembic y comentar estas líneas.
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Base de datos sincronizada (Modo Desarrollo).")
    
    logger.info(f"Iniciando Audit Service en entorno: {settings.ENVIRONMENT}")
    yield
    
    # Shutdown: Liberar recursos de base de datos
    await engine.dispose()
    logger.info("Recursos liberados. Apagando servicio.")


# Instancia de FastAPI

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None, # Ocultar docs en prod (OWASP)
    redoc_url=None
)

# CORS: Configurado de forma restrictiva
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://tu-dominio-interno.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"], # El Audit Service NO permite PUT ni DELETE por diseño
    allow_headers=["Authorization", "Content-Type", "X-Forwarded-For"],
)

# Incluir Rutas
app.include_router(audit_router, prefix=settings.API_V1_STR)

# Global Exception Handlers (OWASP Safe Error Handling)

@app.exception_handler(AuditServiceException)
async def audit_service_exception_handler(request: Request, exc: AuditServiceException):
    """Maneja errores controlados del servicio. Separa logs internos del mensaje al cliente."""
    logger.error(f"AuditServiceException: {exc.internal_message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail} # Mensaje sanitizado y seguro
    )

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """Maneja violaciones de reglas de negocio en la capa de Dominio."""
    logger.warning(f"DomainException: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Atrapa cualquier error no controlado (ej. caída de BD, error de sintaxis).
    NUNCA devuelve el stacktrace al cliente (Prevención de Information Leakage).
    """
    logger.critical(f"Unhandled Exception: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno en el servidor. El incidente ha sido registrado."}
    )

# Endpoint de Salud (Liveness Probe para Kubernetes/Docker)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}