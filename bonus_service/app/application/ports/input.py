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
class CalculateBonusCommand:
    """
    DTO para cálculo individual de bono.
    
    Representa la intención del cliente de calcular un bono.
    No contiene validaciones (esas están en la capa de infraestructura).
    """
    evaluacion_id: uuid.UUID
    salario_base_snapshot: float
    impacto_ebitda_logrado: float
    calificacion_global: Optional[float] = None


@dataclass(frozen=True)
class CalculateBonusBatchCommand:
    """DTO para cálculo masivo de bonos."""
    registros: List[dict]


@dataclass(frozen=True)
class AuditContext:
    """DTO para contexto de auditoría (LFPDPPP Art. 18-19)."""
    user_id: str
    client_ip: Optional[str] = None
    resource_id: Optional[str] = None


class CalculateBonusInputPort(ABC):
    """Puerto de entrada para cálculo de bono individual."""
    @abstractmethod
    async def execute(self, command: CalculateBonusCommand, audit_context: AuditContext) -> dict:
        ...


class CalculateBonusBatchInputPort(ABC):
    """Puerto de entrada para cálculo masivo de bonos."""
    @abstractmethod
    async def execute(self, command: CalculateBonusBatchCommand, audit_context: AuditContext) -> dict:
        ...


class GetBonusReportInputPort(ABC):
    """Puerto de entrada para generación de reportes."""
    @abstractmethod
    async def execute(self, periodo_id: int) -> List[dict]:
        ...
