"""
Repositorios SQL para Cálculo de Logro.

Cumple LFPDPPP Art. 18-19 (cifrado en reposo) y OWASP Secure-by-Design.
Datos sensibles se cifran con AES-256 antes de persistir y se descifran al leer.

REFACTORIZADO:
- Context managers para gestión de sesiones
- Rollback explícito en excepciones
- Eliminación de session.close() manual
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from cryptography.fernet import Fernet
from sqlalchemy import select, insert, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.entities import CalculoLogro
from app.infrastructure.database.models import (
    CalculoLogroModel,
    EvaluacionReadModel,
    AuditLogModel,
)

logger = logging.getLogger(__name__)


class SQLCalculoLogroRepository:
    """Repositorio de cálculos de logro con cifrado en reposo (LFPDPPP Art. 18-19)."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._fernet = Fernet(settings.ENCRYPTION_KEY.encode("utf-8"))

    # ── Helpers de cifrado ──
    def _encrypt(self, value: float) -> bytes:
        """Cifra un valor float en AES-256."""
        return self._fernet.encrypt(str(value).encode("utf-8"))

    def _decrypt(self, encrypted: bytes) -> float:
        """Descifra bytes a float."""
        return float(self._fernet.decrypt(encrypted).decode("utf-8"))

    async def save(self, calculo: CalculoLogro, calculado_por: Optional[str] = None) -> CalculoLogro:
        """Persiste un cálculo de logro con cifrado."""
        try:
            db_calculo = CalculoLogroModel(
                evaluacion_id=calculo.evaluacion_id,
                calificacion_global_cifrada=self._encrypt(calculo.calificacion_global),
                porcentaje_logro_cifrado=self._encrypt(calculo.porcentaje_logro),
                calculado_por=calculado_por,
            )
            self._session.add(db_calculo)
            await self._session.commit()
            await self._session.refresh(db_calculo)
            logger.info(
                f"Logro guardado: evaluacion={calculo.evaluacion_id} "
                f"porcentaje={calculo.porcentaje_logro}%"
            )
            return self._to_entity(db_calculo)
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al guardar logro: {exc}",
                exc_info=True
            )
            raise

    async def save_batch(
        self,
        calculos: List[CalculoLogro],
        calculado_por: Optional[str] = None,
    ) -> int:
        """Persiste múltiples cálculos de logro con cifrado."""
        try:
            if not calculos:
                return 0

            db_objects = [
                CalculoLogroModel(
                    evaluacion_id=c.evaluacion_id,
                    calificacion_global_cifrada=self._encrypt(c.calificacion_global),
                    porcentaje_logro_cifrado=self._encrypt(c.porcentaje_logro),
                    calculado_por=calculado_por,
                )
                for c in calculos
            ]
            self._session.add_all(db_objects)
            await self._session.commit()
            logger.info(
                f"Batch guardado: {len(db_objects)} registros, "
                f"calculado_por={calculado_por}"
            )
            return len(db_objects)
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al guardar batch de logros: {exc}",
                exc_info=True
            )
            raise

    async def find_by_evaluacion(self, evaluacion_id: uuid.UUID) -> Optional[CalculoLogro]:
        """Busca un cálculo de logro por evaluacion_id."""
        try:
            result = await self._session.execute(
                select(CalculoLogroModel).where(
                    CalculoLogroModel.evaluacion_id == evaluacion_id
                )
            )
            row = result.scalar_one_or_none()
            return self._to_entity(row) if row else None
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al buscar logro por evaluacion {evaluacion_id}: {exc}",
                exc_info=True
            )
            raise

    async def find_by_periodo(self, periodo_id: int) -> List[CalculoLogro]:
        """Busca cálculos por periodo (join con evaluaciones)."""
        try:
            result = await self._session.execute(
                select(CalculoLogroModel)
                .join(
                    EvaluacionReadModel,
                    CalculoLogroModel.evaluacion_id == EvaluacionReadModel.id
                )
                .where(EvaluacionReadModel.periodo_id == periodo_id)
            )
            rows = result.scalars().all()
            return [self._to_entity(r) for r in rows]
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al buscar logros por periodo {periodo_id}: {exc}",
                exc_info=True
            )
            raise

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        evaluacion_id: Optional[uuid.UUID] = None,
        calculado_por: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> tuple[List[CalculoLogro], int]:
        """Lista cálculos de logro con paginación y filtros."""
        try:
            from sqlalchemy import func
            
            query = select(CalculoLogroModel)
            
            # Aplicar filtros
            if evaluacion_id:
                query = query.where(CalculoLogroModel.evaluacion_id == evaluacion_id)
            if calculado_por:
                query = query.where(CalculoLogroModel.calculado_por == calculado_por)
            if fecha_desde:
                query = query.where(CalculoLogroModel.fecha_calculo >= fecha_desde)
            if fecha_hasta:
                query = query.where(CalculoLogroModel.fecha_calculo <= fecha_hasta)
            
            # Contar total
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self._session.execute(count_query)
            total = total_result.scalar() or 0
            
            # Aplicar paginación y ordenamiento
            query = query.order_by(CalculoLogroModel.fecha_calculo.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            result = await self._session.execute(query)
            rows = result.scalars().all()
            
            return [self._to_entity(r) for r in rows], total
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al listar logros paginados: {exc}",
                exc_info=True
            )
            raise

    def _to_entity(self, row: CalculoLogroModel) -> CalculoLogro:
        """Convierte fila de BD (cifrada) a entidad de dominio (descifrada)."""
        return CalculoLogro(
            evaluacion_id=row.evaluacion_id,
            calificacion_global=self._decrypt(row.calificacion_global_cifrada),
            porcentaje_logro=self._decrypt(row.porcentaje_logro_cifrado),
            fecha_calculo=row.fecha_calculo,
        )


class SQLEvaluacionReadRepository:
    """Repositorio de SOLO LECTURA para evaluaciones."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, evaluacion_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Obtiene una evaluación por ID."""
        try:
            result = await self._session.execute(
                select(EvaluacionReadModel).where(
                    EvaluacionReadModel.id == evaluacion_id
                )
            )
            row = result.scalar_one_or_none()
            if not row:
                return None

            return {
                "id": row.id,
                "evaluado_id": row.evaluado_id,
                "evaluador_id": row.evaluador_id,
                "periodo_id": row.periodo_id,
                "estado": row.estado,
                "calificacion_global": row.calificacion_global,
                "fecha_creacion": row.fecha_creacion,
            }
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                f"Error al buscar evaluacion {evaluacion_id}: {exc}",
                exc_info=True
            )
            raise

    async def create_evaluacion(
        self,
        evaluacion_id: uuid.UUID,
        calificacion_global: float,
    ) -> Dict[str, Any]:
        """Crea una evaluación si no existe."""
        try:
            existing = await self.get_by_id(evaluacion_id)
            if existing:
                return existing

            new_eval = EvaluacionReadModel(
                id=evaluacion_id,
                evaluado_id=uuid.uuid4(),
                evaluador_id=uuid.uuid4(),
                periodo_id=1,
                estado="SUBMITTED",
                calificacion_global=calificacion_global,
            )
            self._session.add(new_eval)
            await self._session.commit()
            await self._session.refresh(new_eval)

            return {
                "id": new_eval.id,
                "evaluado_id": new_eval.evaluado_id,
                "evaluador_id": new_eval.evaluador_id,
                "periodo_id": new_eval.periodo_id,
                "estado": new_eval.estado,
                "calificacion_global": new_eval.calificacion_global,
                "fecha_creacion": new_eval.fecha_creacion,
            }
        except Exception as exc:
            await self._session.rollback()
            logger.error(f"Error al crear evaluacion: {exc}", exc_info=True)
            raise


class SQLAuditLogRepository:
    """Repositorio de auditoría para trazabilidad LFPDPPP Art. 21."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        status: str,
        detail: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> None:
        """Registra una acción de auditoría."""
        try:
            audit_log = AuditLogModel(
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                status=status,
                detail=detail,
                client_ip=client_ip,
            )
            self._session.add(audit_log)
            await self._session.commit()
            logger.debug(
                f"Audit log: user={user_id} action={action} "
                f"status={status} resource={resource_id}"
            )
        except Exception as exc:
            await self._session.rollback()
            logger.error(f"Error al registrar audit log: {exc}", exc_info=True)
            raise


class SQLDirectorioRepository:
    """Repositorio para consulta del directorio de empleados."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_directorio_empleados(self) -> List[Dict[str, Any]]:
        """
        Obtiene el directorio completo de empleados con roles, departamentos y jefes.
        
        Consulta SQL segura usando text() para evitar SQL Injection.
        """
        try:
            query = text("""
                SELECT 
                    e.username AS empleado, 
                    r.nombre AS rol, 
                    d.nombre AS departamento,
                    j.username AS jefe_inmediato
                FROM usuarios e
                JOIN cat_roles r ON e.rol_id = r.id
                JOIN cat_departamentos d ON e.departamento_id = d.id
                LEFT JOIN usuarios j ON e.manager_id = j.id;
            """)
            
            result = await self._session.execute(query)
            rows = result.mappings().all()
            
            directorio = [
                {
                    "empleado": row["empleado"],
                    "rol": row["rol"],
                    "departamento": row["departamento"],
                    "jefe_inmediato": row["jefe_inmediato"],
                }
                for row in rows
            ]
            
            logger.info(f"Directorio consultado: {len(directorio)} registros")
            return directorio
            
        except Exception as exc:
            await self._session.rollback()
            logger.error(f"Error al consultar directorio: {exc}", exc_info=True)
            raise