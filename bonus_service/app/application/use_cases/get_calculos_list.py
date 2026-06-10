"""
Use Case: Listado paginado de cálculos de logro.
Cumple: OWASP Secure-by-Design + LFPDPPP Art. 21 (trazabilidad).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from app.application.ports.output import LogroRepositoryPort
from app.domain.entities import CalculoLogro


class GetCalculosListUseCase:
    """
    Caso de uso para listado paginado de cálculos de logro con filtros.

    CUMPLIMIENTO:
    - LFPDPPP Art. 21: Trazabilidad de consultas
    - OWASP Secure-by-Design: Validación de entrada, paginación para prevenir DoS
    """

    def __init__(self, logro_repo: LogroRepositoryPort):
        self._logro_repo = logro_repo

    async def execute(
        self,
        page: int = 1,
        page_size: int = 20,
        evaluacion_id: Optional[uuid.UUID] = None,
        calculado_por: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> tuple[List, int]:
        """
        Ejecuta el listado paginado con filtros.

        Args:
            page: Número de página (1-indexed)
            page_size: Tamaño de página (máx 100)
            evaluacion_id: Filtrar por UUID de evaluación
            calculado_por: Filtrar por usuario que realizó el cálculo
            fecha_desde: Fecha desde (inclusive)
            fecha_hasta: Fecha hasta (inclusive)

        Returns:
            tuple: (lista de CalculoLogro, total de registros)
        """
        # Validaciones de entrada (OWASP Input Validation)
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        # Validar rango de fechas
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise ValueError("fecha_desde no puede ser mayor que fecha_hasta")

        # Delegar al repositorio
        calculos, total = await self._logro_repo.list_paginated(
            page=page,
            page_size=page_size,
            evaluacion_id=evaluacion_id,
            calculado_por=calculado_por,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        return calculos, total