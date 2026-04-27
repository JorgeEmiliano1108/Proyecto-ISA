import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import BonusCalculation


class BonusRepositoryPort(ABC):
    """Contrato de escritura sobre la tabla bonos."""

    @abstractmethod
    async def save(self, bonus: BonusCalculation) -> BonusCalculation:
        ...

    @abstractmethod
    async def save_batch(self, bonuses: List[BonusCalculation]) -> int:
        ...

    @abstractmethod
    async def find_by_evaluacion(self, evaluacion_id: uuid.UUID) -> Optional[BonusCalculation]:
        ...

    @abstractmethod
    async def find_by_periodo(self, periodo_id: int) -> List[BonusCalculation]:
        ...


class EvaluacionReadRepositoryPort(ABC):
    """Contrato de SOLO LECTURA sobre la tabla evaluaciones."""

    @abstractmethod
    async def get_by_id(self, evaluacion_id: uuid.UUID) -> Optional[dict]:
        """Retorna la evaluación con su calificacion_global y datos relevantes."""
        ...

    @abstractmethod
    async def create_evaluacion(
        self,
        evaluacion_id: uuid.UUID,
        calificacion_global: float,
    ) -> dict:
        """Crea una evaluación si no existe (para permitir cálculo de bono)."""
        ...


class AuditLogRepositoryPort(ABC):
    """Contrato para registro de auditoría (LFPDPPP Art. 18-19)."""

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str | None,
        status: str,
        detail: str | None = None,
        client_ip: str | None = None,
    ) -> None:
        """Registra una acción sin almacenar datos sensibles."""
        ...
