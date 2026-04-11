# app/infrastructure/database/models.py
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.entities import EvaluationStatus, ActorRole

class Base(DeclarativeBase):
    pass

class WorkflowModel(Base):
    """Tabla principal que guarda el estado de la evaluación."""
    __tablename__ = "evaluation_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ID de la evaluación que vive en el microservicio de Django
    evaluation_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    status: Mapped[EvaluationStatus] = mapped_column(SQLEnum(EvaluationStatus), default=EvaluationStatus.DRAFT, nullable=False)
    requires_manager: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    justification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relación 1 a Muchos: Un workflow tiene muchas firmas
    # cascade="all, delete-orphan" limpia las firmas hijas si se borran de la lista
    signatures: Mapped[List["SignatureModel"]] = relationship(
        back_populates="workflow", 
        cascade="all, delete-orphan"
    )


class SignatureModel(Base):
    """Tabla secundaria que guarda las firmas criptográficas de los evaluadores."""
    __tablename__ = "approval_signatures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evaluation_workflows.id"), nullable=False, index=True)
    
    actor_id: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_role: Mapped[ActorRole] = mapped_column(SQLEnum(ActorRole), nullable=False)
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    signature_data: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)

    workflow: Mapped["WorkflowModel"] = relationship(back_populates="signatures")