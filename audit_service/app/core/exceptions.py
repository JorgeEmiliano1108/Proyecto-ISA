# app/core/exceptions.py
from typing import Optional
from fastapi import status

class AuditServiceException(Exception):
    """
    Excepción base para todo el microservicio.
    Implementa el patrón de Seguridad OWASP: "Safe Error Messages".
    """
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        internal_message: Optional[str] = None
    ):
        self.status_code = status_code
        self.detail = detail  # Mensaje seguro que se expone en la API (Safe for client)
        self.internal_message = internal_message or detail  # Detalle técnico para logs internos
        super().__init__(self.detail)



# Excepciones de Seguridad y Acceso (RBAC / Auth)


class UnauthorizedException(AuditServiceException):
    def __init__(self, internal_message: str = "Token ausente o inválido."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida para realizar esta acción.",
            internal_message=internal_message
        )

class ForbiddenException(AuditServiceException):
    def __init__(self, internal_message: str = "Rol insuficiente para la operación."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene los permisos necesarios para acceder a este recurso.",
            internal_message=internal_message
        )



# Excepciones de Integridad y Dominio (Tamper-Evidence / LFPDPPP)


class LogTamperingDetectedException(AuditServiceException):
    """
    Se lanza cuando la verificación HMAC de un log falla. 
    ¡ALERTA CRÍTICA DE SEGURIDAD!
    """
    def __init__(self, log_id: str, internal_message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Se detectó una inconsistencia de integridad en el registro solicitado.",
            internal_message=f"Tampering Detectado en Log ID {log_id}: {internal_message}"
        )

class InvalidLogPayloadException(AuditServiceException):
    """
    Se lanza cuando un microservicio intenta enviar un log con estructura inválida 
    que no cumple con la minimización o trazabilidad mínima.
    """
    def __init__(self, internal_message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El formato del registro de auditoría no cumple con los criterios de aceptación.",
            internal_message=internal_message
        )



# Excepciones de Recursos

class ResourceNotFoundException(AuditServiceException):
    def __init__(self, resource_name: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            # Mensaje genérico para no confirmar/denegar la existencia de datos a escaneadores ciegos
            detail=f"El recurso solicitado no fue encontrado o no está disponible.", 
            internal_message=f"{resource_name} con ID {resource_id} no encontrado en base de datos."
        )