# app/application/ports/input.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IApproveEvaluationUseCase(ABC):
    """
    Puerto de Entrada (Contrato) para el caso de uso de aprobar una evaluación.
    Aísla la capa de infraestructura (FastAPI) de la implementación de negocio.
    """
    @abstractmethod
    async def execute(
        self, 
        evaluation_id: str, 
        actor_id: str, 
        signature_data: str, 
        ip_address: str
    ) -> Dict[str, Any]:
        """Ejecuta el flujo de aprobación y retorna un diccionario con el resultado."""
        pass


class IRejectEvaluationUseCase(ABC):
    """
    Puerto de Entrada (Contrato) para el caso de uso de rechazar una evaluación.
    """
    @abstractmethod
    async def execute(
        self, 
        evaluation_id: str, 
        actor_id: str, 
        justification: str, 
        ip_address: str
    ) -> Dict[str, Any]:
        """Ejecuta el flujo de rechazo y retorna un diccionario con el resultado."""
        pass