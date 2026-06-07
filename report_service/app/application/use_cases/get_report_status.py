"""app/application/use_cases/get_report_status.py

Caso de uso para consultar el estado de un job de generación de reporte.
Implementa GetReportStatusInputPort para mantener la Arquitectura Hexagonal.
"""

import logging

from app.application.ports.input import GetReportStatusInputPort
from app.application.ports.output import JobStorePort

logger = logging.getLogger("ms_reports.use_case")

class GetReportStatusUseCase(GetReportStatusInputPort):
    def __init__(self, job_store: JobStorePort):
        self.job_store = job_store

    def execute(self, job_id: str) -> dict:
        """
        Consulta el estado actual de un job de generación de reporte
        y retorna la URL de descarga si está completo.
        """
        try:
            result_url = None
            status = "UNKNOWN"

            job_data = self.job_store.get_job(job_id)
            if not job_data:
                return {"job_id": job_id, "status": "NOT_FOUND", "download_url": None}

            status = job_data.get("status", "UNKNOWN")
            result_url = job_data.get("result", None)

            return {
                "job_id": job_id,
                "status": status,
                "download_url": result_url
            }
        except Exception as exc:
            logger.error(f"Error consultando estado del job {job_id}: {exc}")
            return {
                "job_id": job_id,
                "status": "ERROR",
                "download_url": None
            }
