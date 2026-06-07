"""app/infrastructure/adapters/http_repository.py

Adaptador HTTP que implementa ISARepositoryPort consultando la API REST del backend Django
en vez de conectar directamente a Supabase.

Resuelve el acoplamiento directo a Supabase desde microservicios.
"""

import logging
import httpx
from typing import Optional
from datetime import datetime

from app.application.ports.output import ISARepositoryPort
from app.domain.entities import EvaluacionISA, EmpleadoBasico, CompetenciaEvaluada
from app.core.config import settings

logger = logging.getLogger("ms_reports.http_repo")

class HttpISARepository(ISARepositoryPort):
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.internal_token = settings.BACKEND_INTERNAL_TOKEN

    def get_evaluation_full_data(self, evaluacion_id: str, requester_id: str, requester_role: str) -> Optional[EvaluacionISA]:
        url = f"{self.base_url}/api/v1/evaluations/{evaluacion_id}/"
        try:
            resp = httpx.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.internal_token}",
                    "Accept": "application/json"
                },
                timeout=15.0
            )
            if resp.status_code == 404:
                logger.warning(f"Evaluación no encontrada: {evaluacion_id}")
                return None
            if resp.status_code == 403:
                logger.warning(f"Acceso denegado a evaluación: {evaluacion_id}")
                return None
            resp.raise_for_status()
            data = resp.json()
            return self._map_to_entity(data)
        except httpx.TimeoutException:
            logger.error(f"Timeout al consultar backend Django para evaluación {evaluacion_id}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Error de conexión al backend Django: {e}")
            return None

    def save_audit_log(self, job_id: str, status: str, result_url: Optional[str] = None, error: Optional[str] = None) -> None:
        try:
            httpx.post(
                f"{self.base_url}/api/v1/reports-audit/",
                headers={
                    "Authorization": f"Bearer {self.internal_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "job_id": job_id,
                    "status": status,
                    "result_url": result_url or "",
                    "error_message": error or ""
                },
                timeout=10.0
            )
        except Exception as e:
            logger.error(f"Error guardando auditoría en backend: {e}")

    def _map_to_entity(self, data: dict) -> EvaluacionISA:
        evaluado = EmpleadoBasico(
            id=data.get("evaluado", ""),
            username=data.get("evaluado_nombre", ""),
            departamento="",
            rol=""
        )
        evaluador = EmpleadoBasico(
            id=data.get("evaluador", ""),
            username=data.get("evaluador_nombre", ""),
            departamento="",
            rol=""
        )
        competencias = []
        for c in data.get("competencias", []):
            competencias.append(CompetenciaEvaluada(
                nombre=c.get("competencia_nombre", ""),
                calificacion=c.get("calificacion", 0),
                comentario=c.get("comentario", "")
            ))
        fecha_str = data.get("fecha_creacion") or data.get("fecha_actualizacion")
        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")) if fecha_str else datetime.now()

        return EvaluacionISA(
            evaluacion_id=data.get("id", ""),
            evaluado=evaluado,
            evaluador=evaluador,
            estado=data.get("estado", ""),
            calificacion_global=float(data["calificacion_global"]) if data.get("calificacion_global") else None,
            logros_previos=data.get("logros_previos"),
            comentarios_evaluador=data.get("comentarios_evaluador"),
            comentarios_evaluado=data.get("comentarios_evaluado"),
            competencias=competencias,
            fecha_creacion=fecha
        )
