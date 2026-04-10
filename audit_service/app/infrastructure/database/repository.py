# app/infrastructure/database/repository.py
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AuditLog
from app.application.ports.output import AuditRepositoryPort
from app.infrastructure.database.models import AuditLogModel

class AuditRepository(AuditRepositoryPort):
    """
    Implementación concreta de PostgreSQL para el puerto de persistencia de auditoría.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------------
    # Mapeadores (Data Mappers): DB Model <-> Domain Entity
    # ---------------------------------------------------------
    def _to_domain(self, db_model: AuditLogModel) -> AuditLog:
        """Convierte una fila de la BD a una Entidad de Dominio inmutable."""
        return AuditLog(
            id=db_model.id,
            actor_id=db_model.actor_id,
            action=db_model.action,
            resource_id=db_model.resource_id,
            resource_type=db_model.resource_type,
            ip_address=db_model.ip_address,
            timestamp=db_model.timestamp,
            details=db_model.details,
            signature=db_model.signature
        )

    def _to_db_model(self, domain_entity: AuditLog) -> AuditLogModel:
        """Convierte la Entidad de Dominio a un modelo de SQLAlchemy."""
        return AuditLogModel(
            id=domain_entity.id,
            actor_id=domain_entity.actor_id,
            action=domain_entity.action,
            resource_id=domain_entity.resource_id,
            resource_type=domain_entity.resource_type,
            ip_address=str(domain_entity.ip_address), # IPAddress de Pydantic a string
            timestamp=domain_entity.timestamp,
            details=domain_entity.details,
            signature=domain_entity.signature
        )

    # ---------------------------------------------------------
    # Implementación de la Interfaz (Port)
    # ---------------------------------------------------------
    async def save(self, log: AuditLog) -> AuditLog:
        """
        Persiste el registro. Lanza excepciones de SQLAlchemy si algo falla.
        """
        db_model = self._to_db_model(log)
        self.session.add(db_model)
        await self.session.commit()
        # No hacemos db.refresh() porque la entidad de dominio ya es la fuente de verdad (inmutable)
        return log

    async def get_by_id(self, log_id: UUID) -> Optional[AuditLog]:
        query = select(AuditLogModel).where(AuditLogModel.id == log_id)
        result = await self.session.execute(query)
        db_model = result.scalar_one_or_none()
        
        if db_model:
            return self._to_domain(db_model)
        return None

    async def get_history_by_resource(self, resource_id: UUID) -> List[AuditLog]:
        """
        Obtiene el historial ordenado de más reciente a más antiguo.
        El índice compuesto 'ix_audit_logs_resource_time' hace que esto sea instantáneo.
        """
        query = (
            select(AuditLogModel)
            .where(AuditLogModel.resource_id == resource_id)
            .order_by(AuditLogModel.timestamp.desc())
        )
        result = await self.session.execute(query)
        db_models = result.scalars().all()
        
        return [self._to_domain(model) for model in db_models]