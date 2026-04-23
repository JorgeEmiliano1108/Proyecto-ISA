import uuid
from decimal import Decimal
from typing import List, Optional

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output import BonusRepositoryPort, EvaluacionReadRepositoryPort, AuditLogRepositoryPort
from app.core.config import settings
from app.domain.entities import BonusCalculation
from app.infrastructure.database.models import BonusModel, EvaluacionReadModel, AuditLogModel


class SQLBonusRepository(BonusRepositoryPort):
    """Implementación SQL del puerto de escritura para bonos.
    
    Cumple LFPDPPP Art. 18-19 (cifrado en reposo) y OWASP Secure-by-Design Domain 3.
    Datos sensibles se cifran con AES-256 antes de persistir y se descifran al leer.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        # Clave de cifrado (debe venir de Docker Secret / Vault / .env)
        # Generar con: Fernet.generate_key().decode()
        self._fernet = Fernet(settings.ENCRYPTION_KEY.encode("utf-8"))

    # ----------------------------------------------------------------------
    # Helpers de cifrado (nunca exponer fuera del repositorio)
    # ----------------------------------------------------------------------
    def _encrypt_decimal(self, value: Decimal) -> bytes:
        """Cifra Decimal sensible (salario o monto)."""
        if value is None:
            return b""
        return self._fernet.encrypt(str(value).encode("utf-8"))

    def _decrypt_decimal(self, encrypted: Optional[bytes]) -> Decimal:
        """Descifra bytes a Decimal."""
        if not encrypted:
            return Decimal("0.00")
        return Decimal(self._fernet.decrypt(encrypted).decode("utf-8"))

    async def save(
        self,
        bonus: BonusCalculation,
        calculado_por: Optional[str] = None,   # ← user_id del JWT
    ) -> BonusCalculation:
        db_bonus = BonusModel(
            evaluacion_id=bonus.evaluacion_id,
            # ── CAMPOS CIFRADOS ──
            salario_base_snapshot=self._encrypt_decimal(bonus.salario_base_snapshot),
            monto_final_bono=self._encrypt_decimal(bonus.monto_final_bono),
            # ── Campos en claro ──
            impacto_ebitda_logrado=bonus.impacto_ebitda_logrado,
            performance_index=bonus.performance_index,
            fecha_calculo=bonus.fecha_calculo,
            calculado_por=calculado_por,
        )
        self._session.add(db_bonus)
        await self._session.commit()
        await self._session.refresh(db_bonus)
        return bonus

    async def save_batch(
        self,
        bonuses: List[BonusCalculation],
        calculado_por: Optional[str] = None,   # mismo usuario o "batch_system"
    ) -> int:
        db_objects = [
            BonusModel(
                evaluacion_id=b.evaluacion_id,
                salario_base_snapshot=self._encrypt_decimal(b.salario_base_snapshot),
                monto_final_bono=self._encrypt_decimal(b.monto_final_bono),
                impacto_ebitda_logrado=b.impacto_ebitda_logrado,
                performance_index=b.performance_index,
                fecha_calculo=b.fecha_calculo,
                calculado_por=calculado_por,
            )
            for b in bonuses
        ]
        self._session.add_all(db_objects)
        await self._session.commit()
        return len(db_objects)

    async def find_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> Optional[BonusCalculation]:
        result = await self._session.execute(
            select(BonusModel).where(BonusModel.evaluacion_id == evaluacion_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def find_by_periodo(self, periodo_id: int) -> List[BonusCalculation]:
        result = await self._session.execute(
            select(BonusModel)
            .join(EvaluacionReadModel, BonusModel.evaluacion_id == EvaluacionReadModel.id)
            .where(EvaluacionReadModel.periodo_id == periodo_id)
        )
        rows = result.scalars().all()
        return [self._to_entity(r) for r in rows]

    def _to_entity(self, row: BonusModel) -> BonusCalculation:
        """Convierte fila de BD (cifrada) a entidad de dominio (descifrada)."""
        return BonusCalculation(
            evaluacion_id=row.evaluacion_id,
            salario_base_snapshot=self._decrypt_decimal(row.salario_base_snapshot),
            impacto_ebitda_logrado=Decimal(str(row.impacto_ebitda_logrado)),
            performance_index=Decimal(str(row.performance_index)),
            monto_final_bono=self._decrypt_decimal(row.monto_final_bono),
            fecha_calculo=row.fecha_calculo,
        )


class SQLEvaluacionReadRepository(EvaluacionReadRepositoryPort):
    """Implementación SQL del puerto de SOLO LECTURA para evaluaciones.
    Sin cambios (no contiene datos sensibles).
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, evaluacion_id: uuid.UUID) -> Optional[dict]:
        result = await self._session.execute(
            select(EvaluacionReadModel).where(EvaluacionReadModel.id == evaluacion_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return {
            "id": str(row.id),
            "evaluado_id": str(row.evaluado_id),
            "periodo_id": row.periodo_id,
            "estado": row.estado,
            "calificacion_global": float(row.calificacion_global) if row.calificacion_global else None,
        }


class SQLAuditLogRepository(AuditLogRepositoryPort):
    """Implementación SQL del puerto de auditoría.
    
    Cumple LFPDPPP Art. 18-19 (trazabilidad) y OWASP A09 (Security Logging).
    NO almacena datos sensibles - solo metadatos de la operación.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str | None,
        status: str,
        detail: str | None = None,
        client_ip: str | None = None,
    ) -> None:
        """Registra una acción en la tabla de auditoría."""
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