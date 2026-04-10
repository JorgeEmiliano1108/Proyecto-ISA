# app/application/ports/output.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.domain.entities import AuditLog

class AuditRepositoryPort(ABC):
    """
    Puerto de Salida para persistencia. 
    Cualquier adaptador de base de datos (SQLAlchemy, Mongo, etc.) debe implementar esto.
    """
    
    @abstractmethod
    async def save(self, log: AuditLog) -> AuditLog:
        """Guarda un registro inmutable en la base de datos."""
        pass

    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> Optional[AuditLog]:
        """Recupera un registro específico por su ID."""
        pass

    @abstractmethod
    async def get_history_by_resource(self, resource_id: UUID) -> List[AuditLog]:
        """Recupera el historial de un recurso (ej. una evaluación)."""
        pass

class EventPublisherPort(ABC):
    """
    Puerto de Salida para mensajería asíncrona (Event-Driven).
    Permite notificar a otros sistemas (como tu IA de Validación de Procesos) 
    sin acoplar el código.
    """
    
    @abstractmethod
    async def publish_audit_event(self, event_name: str, log: AuditLog) -> None:
        """
        Emite un evento a un message broker (Redis Pub/Sub, RabbitMQ, Kafka).
        Implementa el patrón 'Fire and Forget'.
        """
        pass