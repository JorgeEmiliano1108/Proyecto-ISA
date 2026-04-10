# app/application/ports/input.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID
from app.domain.entities import AuditLog

class RecordAuditLogInputPort(ABC):
    """
    Puerto de Entrada: Contrato para registrar un log.
    FastAPI dependerá de esta abstracción, no de la implementación concreta.
    """
    @abstractmethod
    async def execute(
        self, 
        actor_id: UUID, 
        action: str, 
        resource_type: str, 
        ip_address: str, 
        details: Dict[str, Any],
        resource_id: Optional[UUID] = None
    ) -> AuditLog:
        pass

class GetAuditHistoryInputPort(ABC):
    """
    Puerto de Entrada: Contrato para consultar el historial de auditoría.
    """
    @abstractmethod
    async def execute(
        self, 
        resource_id: UUID, 
        requester_role: str
    ) -> List[AuditLog]:
        pass