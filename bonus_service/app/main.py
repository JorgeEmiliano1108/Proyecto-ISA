"""
Punto de entrada de la aplicación FastAPI.
Cumple: OWASP Secure-by-Design Framework + OWASP SCP + LFPDPPP.

CONFIGURACIÓN DE SEGURIDAD:
- Headers de seguridad HTTP (HSTS, CSP, X-Frame-Options, etc.)
- Rate Limiting para prevenir ataques de fuerza bruta
- Manejo de errores sin fuga de información
- CORS configurado de forma restrictiva
"""
import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import EXCEPTION_HANDLERS
from app.core.logging import setup_secure_logging, SensitiveDataFilter
from app.infrastructure.api.routers import router
from app.infrastructure.messaging.publisher import event_publisher
from app.infrastructure.api.middleware.rate_limit import rate_limit_middleware


setup_secure_logging()
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que añade headers de seguridad HTTP.
    
    CUMPLIMIENTO OWASP:
    - HSTS: Force HTTPS connections
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: XSS filtering (legacy browsers)
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Restrict browser features
    - Content-Security-Policy: Prevent XSS and injection attacks
    - Cache-Control: Prevent caching of sensitive data
    """
    
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none'"
        ),
        "Cache-Control": "no-store, no-cache, must-revalidate, private",
        "Pragma": "no-cache",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        for header_name, header_value in self.SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
        
        if request.url.path.startswith("/api/"):
            response.headers["Vary"] = "Authorization"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware de logging de requests.
    
    OWASP A09: Security Logging and Monitoring
    - Registra todos los requests sin datos sensibles
    - Filtra información sensible antes de loggear
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        path = request.url.path
        method = request.method
        
        logger.info(f"Request: {method} {path} from {client_ip}")
        
        try:
            response = await call_next(request)
            logger.info(f"Response: {method} {path} → {response.status_code}")
            return response
        except Exception as exc:
            logger.error(f"Request failed: {method} {path} → Error: {type(exc).__name__}")
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para startup/shutdown."""
    logger.info("Iniciando Bonus Service v1.3.0 - OWASP + LFPDPPP Compliant")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")
    
    yield
    
    logger.info("Cerrando Bonus Service")
    await event_publisher.close()


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI con todas las configuraciones.
    """
    app = FastAPI(
        title="Bonus Calculation Service",
        description=(
            "Microservicio matemático del Sistema ISA. "
            "Calcula, persiste y audita bonificaciones corporativas "
            "usando arquitectura hexagonal + procesamiento vectorizado. "
            "\n\n**CUMPLIMIENTO:** LFPDPPP, OWASP SCP, OWASP Secure-by-Design"
        ),
        version="1.3.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG_MODE else None,
        redoc_url="/redoc" if settings.DEBUG_MODE else None,
        openapi_url="/openapi.json" if settings.DEBUG_MODE else None,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.middleware("http")(rate_limit_middleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG_MODE else [],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    for exc_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exc_class, handler)

    app.include_router(router)
    
    return app


app = create_app()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global de excepciones que NO revela stack traces.
    
    OWASP Error Handling: Los errores 500 nunca deben mostrar información
    de infraestructura (stack traces, rutas de archivos, versiones de libs).
    """
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)[:100]}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
        headers={"Cache-Control": "no-store"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG_MODE,
    )