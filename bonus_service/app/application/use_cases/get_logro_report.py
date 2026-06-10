"""
Use Case: Generación de reporte de porcentajes de logro consolidados por periodo.
Cumple: LFPDPPP Art. 18-19 (solo metadatos, no datos sensibles crudos)
"""
import logging
from typing import List

from app.application.ports.output import LogroRepositoryPort


logger = logging.getLogger(__name__)


class GetLogroReportUseCase:
    """
    Caso de uso para generar reporte de logros por periodo.

    CUMPLIMIENTO:
    - LFPDPPP: Solo metadatos (evaluacion_id, porcentaje_logro)
    - OWASP: Sin datos sensibles en el reporte
    """

    def __init__(self, logro_repo: LogroRepositoryPort):
        self._logro_repo = logro_repo

    async def execute(self, periodo_id: int) -> List[dict]:
        """
        Genera reporte de porcentajes de logro por periodo.

        Args:
            periodo_id: ID del periodo a consultar

        Returns:
            List[dict]: Lista de dicts con evaluacion_id y porcentaje_logro
        """
        logros = await self._logro_repo.find_by_periodo(periodo_id)

        # sanitize: solo retornar metadatos (no datos sensibles crudos)
        return [
            {
                "evaluacion_id": str(logro.evaluacion_id),
                "porcentaje_logro": logro.porcentaje_logro,
                "fecha_calculo": logro.fecha_calculo.isoformat(),
            }
            for logro in logros
        ]
