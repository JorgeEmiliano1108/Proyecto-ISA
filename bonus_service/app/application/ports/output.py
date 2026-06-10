"""
Contratos de salida (puertos) para la arquitectura hexagonal.
"""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.entities import CalculoLogro


class LogroRepositoryPort(ABC):
    """Contrato de escritura sobre la tabla de cálculos de logro."""

    @abstractmethod
    async def save(self, calculo: CalculoLogro, calculado_por: Optional[str] = None) -> CalculoLogro:
        """Guarda un cálculo de logro con cifrado de datos sensibles."""
        ...

    @abstractmethod
    async def save_batch(self, calculos: List[CalculoLogro], calculado_por: Optional[str] = None) -> int:
        """Guarda múltiples cálculos de logro. Retorna el número de registros guardados."""
        ...

    @abstractmethod
    async def find_by_evaluacion(self, evaluacion_id: uuid.UUID) -> Optional[CalculoLogro]:
        """Busca un cálculo de logro por su evaluacion_id."""
        ...

    @abstractmethod
    async def find_by_periodo(self, periodo_id: int) -> List[CalculoLogro]:
        """Busca todos los cálculos de logro de un periodo dado."""
        ...

    @abstractmethod
    async def list_paginated(
        self,
        page: int,
        page_size: int,
        evaluacion_id: Optional[uuid.UUID] = None,
        calculado_por: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> tuple[List[CalculoLogro], int]:
        """
        Lista cálculos de logro con paginación y filtros.
        
        Retorna:
            tuple: (lista de cálculos, total de registros)
        """
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
        """Crea una evaluación si no existe (para permitir cálculo de logro)."""
        ...


class AuditLogRepositoryPort(ABC):
    """Contrato para registro de auditoría (LFPDPPP Art. 18-19)."""

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        status: str,
        detail: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> None:
        """Registra una acción sin almacenar datos sensibles."""
        ...
