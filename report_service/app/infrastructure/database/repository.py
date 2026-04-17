"""app/infrastructure/database/repository.py

Adaptador oficial para PostgreSQL en Arquitectura Hexagonal.
Implementa ISARepositoryPort utilizando SQLAlchemy 2.0 y asyncpg.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import text, func
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.application.ports.output import ISARepositoryPort
from app.domain.entities import EvaluacionISA, EmpleadoBasico, CompetenciaEvaluada
from app.infrastructure.database.database import AsyncSessionLocal
from app.infrastructure.database.models import ReportAuditModel

# --- Importamos el Gestor RBAC Centralizado ---
from app.core.rbac import rbac_manager

logger = logging.getLogger("report_service.repository")

class PostgresISARepository(ISARepositoryPort):
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        if not self.db_url:
            logger.warning("DATABASE_URL no configurada. Las operaciones a BD fallarán.")
        else:
            try:
                asyncio.run(self._ensure_audit_table_exists_async())
            except Exception as e:
                logger.error(f"Error al verificar la tabla de auditoría: {e}")

    async def _ensure_audit_table_exists_async(self):
        """Garantiza la existencia de la tabla de auditoría utilizando el motor asíncrono."""
        async with AsyncSessionLocal() as session:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS isa_reports_audit (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    result_url TEXT,
                    error_message TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            await session.commit()

    # =========================================================================
    # IMPLEMENTACIÓN DEL PUERTO DE LECTURA (TRANSACCIONAL) + RBAC + IDOR
    # =========================================================================
    def get_evaluation_full_data(self, evaluacion_id: str, requester_id: str, requester_role: str) -> Optional[EvaluacionISA]:
        return asyncio.run(self._get_evaluation_full_data_async(evaluacion_id, requester_id, requester_role))

    async def _get_evaluation_full_data_async(self, evaluacion_id: str, requester_id: str, requester_role: str) -> Optional[EvaluacionISA]:
        """
        Extrae la evaluación validando IDOR mediante políticas RBAC dinámicas.
        """
        
        # 1. Evaluación Centralizada de Permisos (RBAC)
        can_read_all = rbac_manager.has_permission(requester_role, "evaluations:read:all")
        
        async with AsyncSessionLocal() as session:
            try:
                # 2. Obtener Cabecera (El SQL ya no conoce los nombres de los roles)
                query_eval = text("""
                    SELECT 
                        e.id as evaluacion_id, e.estado, e.calificacion_global, 
                        e.logros_previos, e.comentarios_evaluador, e.comentarios_evaluado, e.fecha_creacion,
                        u1.id as ev_id, u1.username as ev_username, r1.nombre as ev_rol, d1.nombre as ev_depto,
                        u2.id as ma_id, u2.username as ma_username, r2.nombre as ma_rol, d2.nombre as ma_depto,
                        b.monto_final_bono
                    FROM evaluaciones e
                    JOIN usuarios u1 ON e.evaluado_id = u1.id
                    JOIN cat_roles r1 ON u1.rol_id = r1.id
                    JOIN cat_departamentos d1 ON u1.departamento_id = d1.id
                    JOIN usuarios u2 ON e.evaluador_id = u2.id
                    JOIN cat_roles r2 ON u2.rol_id = r2.id
                    JOIN cat_departamentos d2 ON u2.departamento_id = d2.id
                    LEFT JOIN bonos b ON e.id = b.evaluacion_id
                    WHERE e.id = CAST(:eval_id AS UUID)
                      AND (
                          :can_read_all = TRUE OR 
                          e.evaluado_id = CAST(:req_id AS UUID) OR 
                          e.evaluador_id = CAST(:req_id AS UUID)
                      );
                """)
                
                result_eval = await session.execute(query_eval, {
                    "eval_id": evaluacion_id,
                    "req_id": requester_id,
                    "can_read_all": can_read_all # Inyectamos el booleano del RBAC
                })
                eval_row = result_eval.mappings().fetchone()

                if not eval_row:
                    logger.warning(f"Acceso denegado o evaluación inexistente. ID: {evaluacion_id}, Solicitante: {requester_id}, Rol: {requester_role}")
                    return None

                # 2. Obtener Detalles de las Competencias
                query_comp = text("""
                    SELECT cc.nombre, cd.calificacion, cd.comentario
                    FROM competencias_detalle cd
                    JOIN cat_competencias cc ON cd.competencia_id = cc.id
                    WHERE cd.evaluacion_id = CAST(:eval_id AS UUID);
                """)
                
                result_comp = await session.execute(query_comp, {"eval_id": evaluacion_id})
                comp_rows = result_comp.mappings().fetchall()

                # 3. Mapear a Entidades de Dominio Inmutables
                evaluado = EmpleadoBasico(
                    id=str(eval_row['ev_id']), username=eval_row['ev_username'], 
                    rol=eval_row['ev_rol'], departamento=eval_row['ev_depto']
                )
                evaluador = EmpleadoBasico(
                    id=str(eval_row['ma_id']), username=eval_row['ma_username'], 
                    rol=eval_row['ma_rol'], departamento=eval_row['ma_depto']
                )
                competencias = [
                    CompetenciaEvaluada(nombre=r['nombre'], calificacion=r['calificacion'], comentario=r['comentario'])
                    for r in comp_rows
                ]

                return EvaluacionISA(
                    evaluacion_id=str(eval_row['evaluacion_id']),
                    evaluado=evaluado,
                    evaluador=evaluador,
                    estado=eval_row['estado'],
                    calificacion_global=float(eval_row['calificacion_global']) if eval_row.get('calificacion_global') else None,
                    logros_previos=eval_row.get('logros_previos'),
                    comentarios_evaluador=eval_row.get('comentarios_evaluador'),
                    comentarios_evaluado=eval_row.get('comentarios_evaluado'),
                    competencias=competencias,
                    bono_asignado=float(eval_row['monto_final_bono']) if eval_row.get('monto_final_bono') else None,
                    fecha_creacion=eval_row['fecha_creacion']
                )
            except Exception as e:
                logger.error(f"Fallo al extraer datos de evaluación {evaluacion_id}: {e}")
                return None

    def save_audit_log(self, job_id: str, status: str, result_url: Optional[str] = None, error: Optional[str] = None) -> None:
        asyncio.run(self._save_audit_log_async(job_id, status, result_url, error))

    async def _save_audit_log_async(self, job_id: str, status: str, result_url: Optional[str] = None, error: Optional[str] = None) -> None:
        async with AsyncSessionLocal() as session:
            try:
                stmt = insert(ReportAuditModel).values(
                    job_id=job_id, status=status, result_url=result_url, error_message=error
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=['job_id'],
                    set_={
                        'status': stmt.excluded.status,
                        'result_url': func.coalesce(stmt.excluded.result_url, ReportAuditModel.result_url),
                        'error_message': stmt.excluded.error_message,
                        'updated_at': func.now()
                    }
                )
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                logger.error(f"Fallo al guardar log de auditoría para {job_id}: {e}")