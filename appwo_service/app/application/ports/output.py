# app/application/ports/output.py
from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities import EvaluationWorkflowEntity, ActorRole

class IApprovalRepository(ABC):
    """Puerto para interactuar con la persistencia (PostgreSQL en el futuro)."""
    
    @abstractmethod
    async def get_workflow_by_eval_id(self, evaluation_id: str) -> Optional[EvaluationWorkflowEntity]:
        pass

    @abstractmethod
    async def save_workflow(self, workflow: EvaluationWorkflowEntity) -> None:
        pass

class IEventPublisher(ABC):
    """Puerto para publicar eventos asíncronos (Redis en el futuro)."""
    
    @abstractmethod
    async def publish_workflow_event(self, event_type: str, workflow: EvaluationWorkflowEntity, actor_id: str) -> None:
        pass

class IUserServiceClient(ABC):
    """Puerto para consultar roles en el microservicio de usuarios (Active Directory)."""
    
    @abstractmethod
    async def get_actor_role(self, actor_id: str) -> ActorRole:
        pass