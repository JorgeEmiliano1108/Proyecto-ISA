# app/infrastructure/database/models.py
import uuid
from datetime import datetime, timezone 
from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class AuditLogModel(Base):
    """
    Representación del Log de Auditoría en PostgreSQL.
    Solo se permiten inserciones (Append-Only) dictadas por el repositorio.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Puede ser nulo si la acción es a nivel de sistema y no de un recurso específico
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # JSONB permite consultas ultra rápidas sobre la estructura del payload si fuera necesario
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Firma criptográfica para Tamper-Evidence (Seguridad LFPDPPP/OWASP)
    signature: Mapped[str] = mapped_column(String(64), nullable=False)

    # Índices compuestos para optimizar el Caso de Uso `get_history.py` (Alta velocidad de lectura)
    __table_args__ = (
        Index('ix_audit_logs_resource_time', 'resource_id', 'timestamp'),
    )

class AIAnomalyReportModel(Base):
    """
    Guarda el análisis del modelo phi-3 sobre un registro de auditoría.
    """
    __tablename__ = "ai_anomaly_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    
    # El veredicto de la IA
    anomaly_detected: Mapped[bool] = mapped_column(nullable=False)
    confidence_score: Mapped[float] = mapped_column(nullable=True) # Opcional, dependiendo de la IA
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Trazabilidad
    model_used: Mapped[str] = mapped_column(String(50), default="phi-3:mini")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('ix_anomaly_reports_audit_id', 'audit_log_id'),
    )