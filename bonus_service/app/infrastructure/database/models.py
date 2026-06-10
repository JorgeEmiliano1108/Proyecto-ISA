"""
Modelos ORM de SQLAlchemy - Cumplimiento LFPDPPP + OWASP Secure-by-Design.
V2.0.0 — REFACTORIZADO: Solo porcentajes de logro.

CUMPLIMIENTO LFPDPPP:
- Art. 6: Los datos personales deben ser tratados conforme a la Ley
- Art. 18: Medidas de seguridad para datos personales
- Art. 19: Implementación de medidas de seguridad
- Art. 21: Registro de tratamientos (logs de auditoría)

CIFRADO EN REPOSO (AES-256/Fernet):
- Campos sensibles se almacenan cifrados
- El cifrado/des-cifrado se realiza en el Repository (capa de infraestructura)
- La clave de cifrado se gestiona vía Docker Secrets
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    UUID,
    String,
    DateTime,
    func,
    LargeBinary,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class EvaluacionReadModel(Base):
    """
    Modelo de solo lectura para la tabla 'evaluaciones'.
    "This service ONLY reads evaluaciones, never modifies them."
    """
    __tablename__ = "evaluaciones"
    __table_args__ = (
        Index("ix_evaluaciones_periodo_id", "periodo_id"),
        Index("ix_evaluaciones_estado", "estado"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID único de la evaluación"
    )
    evaluado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="UUID del empleado evaluado"
    )
    evaluador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="UUID del evaluador"
    )
    periodo_id: Mapped[int] = mapped_column(
        nullable=False,
        comment="ID del periodo de evaluación"
    )
    estado: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        comment="Estado: DRAFT, SUBMITTED, APPROVED, REJECTED"
    )
    calificacion_global: Mapped[float] = mapped_column(
        nullable=True,
        comment="Calificación global 1.00 - 5.00"
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación del registro"
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Fecha de última modificación"
    )


class CalculoLogroModel(Base):
    """
    Modelo para la tabla 'calculos_logro' — Solo porcentajes de logro.

    CUMPLIMIENTO:
    - LFPDPPP Art. 18-19: Cifrado en reposo para datos sensibles
    - OWASP Data Protection: encryption-at-rest
    """
    __tablename__ = "calculos_logro"
    __table_args__ = (
        Index("ix_cl_evaluacion_id", "evaluacion_id"),
        Index("ix_cl_fecha_calculo", "fecha_calculo"),
        Index("ix_cl_calculado_por", "calculado_por"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID único del cálculo de logro"
    )

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="FK a evaluaciones.id"
    )

    # Calificación del evaluador (cifrada en reposo)
    calificacion_global_cifrada: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="CIFRADO — Calificación global (1.0 - 5.0)"
    )

    # Resultado del cálculo (cifrado en reposo)
    porcentaje_logro_cifrado: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="CIFRADO — Porcentaje de logro calculado"
    )

    fecha_calculo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha y hora del cálculo"
    )

    # Trazabilidad LFPDPPP Art. 21
    calculado_por: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="user_id del token — Trazabilidad"
    )

    def __repr__(self) -> str:
        return f"<CalculoLogro id={self.id} evaluacion={self.evaluacion_id}>"


class AuditLogModel(Base):
    """
    Modelo de auditoría para cumplimiento LFPDPPP Art. 18-19 y 21.

    Registra TODOS los accesos y operaciones realizadas sobre datos sensibles.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_created_at", "created_at"),
        Index("ix_audit_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID único del registro de auditoría"
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="ID del usuario que realizó la acción"
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo de acción: calculate_logro, batch_calculate..."
    )

    resource_id: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="ID del recurso afectado"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Estado: success, failure, blocked, denied"
    )

    detail: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Descripción SIN datos sensibles"
    )

    client_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=True,
        comment="IP del cliente anonimizada"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp de la operación"
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} user={self.user_id} "
            f"action={self.action} status={self.status}>"
        )
