"""
Data Transfer Objects (DTOs) puros para Arquitectura Hexagonal.

Estos DTOs son 100% Python estándar - SIN dependencias de frameworks.
El router FastAPI transforma los schemas Pydantic a estos DTOs antes
de pasarlos a los casos de uso.
"""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CalculateLogroCommand:
    """
    DTO para cálculo individual de porcentaje de logro.

    Representa la intención del cliente de calcular un porcentaje de logro.
    No contiene validaciones (esas están en la capa de infraestructura).
    """
    evaluacion_id: uuid.UUID
    calificacion_global: float


@dataclass(frozen=True)
class CalculateLogroBatchCommand:
    """DTO para cálculo masivo de porcentajes de logro."""
    registros: List[dict]


@dataclass(frozen=True)
class AuditContext:
    """DTO para contexto de auditoría (LFPDPPP Art. 18-19)."""
    user_id: str
    client_ip: Optional[str] = None
    resource_id: Optional[str] = None


class CalculateLogroInputPort(ABC):
    """Puerto de entrada para cálculo de porcentaje de logro individual."""
    @abstractmethod
    async def execute(self, command: CalculateLogroCommand, audit_context: AuditContext) -> dict:
        ...


class CalculateLogroBatchInputPort(ABC):
    """Puerto de entrada para cálculo masivo de porcentajes de logro."""
    @abstractmethod
    async def execute(self, command: CalculateLogroBatchCommand, audit_context: AuditContext) -> dict:
        ...


class GetLogroReportInputPort(ABC):
    """Puerto de entrada para generación de reportes de logro."""
    @abstractmethod
    async def execute(self, periodo_id: int) -> List[dict]:
        ...
