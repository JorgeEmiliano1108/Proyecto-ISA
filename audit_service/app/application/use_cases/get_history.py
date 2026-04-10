# app/application/use_cases/get_history.py
from typing import List
from uuid import UUID

from app.domain.entities import AuditLog
from app.application.ports.input import GetAuditHistoryInputPort
from app.application.ports.output import AuditRepositoryPort
from app.core.exceptions import ForbiddenException, ResourceNotFoundException

# Roles permitidos para leer auditorías de otros recursos (RBAC)
AUTHORIZED_AUDIT_ROLES = {"ADMIN", "AUDITOR", "HR_MANAGER"}

class GetAuditHistoryUseCase(GetAuditHistoryInputPort):
    """
    Caso de Uso: Recuperar el historial inmutable de un recurso.
    Aplica controles de acceso estrictos (RBAC).
    """
    
    def __init__(self, repository: AuditRepositoryPort):
        # Solo inyectamos el repositorio de lectura. No necesitamos el Publisher aquí.
        self.repository = repository

    async def execute(
        self, 
        resource_id: UUID, 
        requester_role: str
    ) -> List[AuditLog]:
        
        # 1. OWASP Access Control (RBAC)
        # Verificamos que el rol del solicitante tenga permisos legales para ver logs.
        if requester_role.upper() not in AUTHORIZED_AUDIT_ROLES:
            raise ForbiddenException(
                internal_message=f"Intento de lectura de auditoría bloqueado. Rol '{requester_role}' no autorizado."
            )

        # 2. Infraestructura: Consultar el repositorio
        history = await self.repository.get_history_by_resource(resource_id)

        # 3. Manejo de recursos vacíos (Safe Error Handling)
        # Si no hay historial, levantamos un 404 genérico para no dar pistas
        # a posibles atacantes sobre si el recurso existe o no en otras bases de datos.
        if not history:
            raise ResourceNotFoundException(
                resource_name="Historial de Auditoría", 
                resource_id=str(resource_id)
            )

        # 4. (Opcional) Verificación de Integridad en Tiempo de Lectura
        # Aquí podríamos recalcular el HMAC de cada log y compararlo con su firma guardada.
        # Si no coincide, levantaríamos un LogTamperingDetectedException. 
        # Por rendimiento, suele hacerse en un Job nocturno, pero si es de altísima seguridad, se hace aquí.

        return history