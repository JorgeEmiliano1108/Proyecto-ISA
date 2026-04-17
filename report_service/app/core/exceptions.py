"""app/core/exceptions.py

Jerarquía centralizada de excepciones para el microservicio de Reportes.
Cumple con OWASP DS-04 (Secure Failures): Estructura los errores con códigos 
internos para el cliente y evita exponer trazas de ejecución (stack traces).
"""
import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("ms_reports.exceptions")

# ============================================================================
# CLASE BASE DE DOMINIO
# ============================================================================
class AppException(Exception):
    """Excepción base de la cual heredan todos los errores del microservicio."""
    def __init__(
        self, 
        message: str, 
        internal_code: str = "ERR_INTERNAL_SERVER", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.internal_code = internal_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DE NEGOCIO E INFRAESTRUCTURA
# ============================================================================
class ResourceNotFoundException(AppException):
    """Lanzada cuando no se encuentra un registro (Evaluación, Regla, Logo)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, 
            internal_code="ERR_RESOURCE_NOT_FOUND", 
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class SecurityForbiddenException(AppException):
    """Lanzada para bloquear intentos de IDOR o violaciones de RBAC."""
    def __init__(self, message: str = "No tienes permisos para acceder a este recurso."):
        super().__init__(
            message=message, 
            internal_code="ERR_SECURITY_FORBIDDEN", 
            status_code=status.HTTP_403_FORBIDDEN
        )

class InfrastructureException(AppException):
    """
    Lanzada cuando falla un adaptador externo (Ollama, MinIO, PostgreSQL).
    El mensaje detallado se guarda en logs, el cliente recibe un mensaje genérico seguro.
    """
    def __init__(self, service: str, safe_message: str = "El servicio externo no está disponible temporalmente."):
        # Registramos el error real en la consola de Docker
        logger.error(f"[INFRA_FAILURE] Falló el adaptador de: {service}")
        
        super().__init__(
            message=safe_message, 
            internal_code=f"ERR_INFRA_{service.upper()}_FAILURE", 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class BusinessValidationException(AppException):
    """Lanzada cuando los datos son correctos en formato, pero violan una regla de negocio."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, 
            internal_code="ERR_BUSINESS_VALIDATION", 
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


# ============================================================================
# MANEJADOR GLOBAL PARA FASTAPI (Intercepta y formatea)
# ============================================================================
async def app_exception_handler(request: Request, exc: AppException):
    """
    Atrapa cualquier AppException lanzada en los endpoints o adaptadores,
    y formatea una respuesta JSON segura y estándar para el cliente.
    """
    # Si es un error 500+, lo registramos en los logs como crítico
    if exc.status_code >= 500:
        logger.critical(f"Error Crítico ({exc.internal_code}): {exc.message} | Detalles: {exc.details}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.internal_code,
                "message": exc.message,
                # En producción, nunca deberíamos enviar stack traces aquí.
                "details": exc.details
            }
        }
    )