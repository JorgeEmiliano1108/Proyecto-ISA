"""
Modelos ORM de SQLAlchemy - Cumplimiento LFPDPPP + OWASP Secure-by-Design.
V1.3.0

CUMPLIMIENTO LFPDPPP:
- Art. 6: Los datos personales deben ser tratados conforme a la Ley
- Art. 18: Medidas de seguridad para datos personales
- Art. 19: Implementación de medidas de seguridad
- Art. 21: Registro de tratamientos (logs de auditoría)

CIFRADO EN REPOSO (AES-256/Fernet):
- Campos sensibles (salario_base_snapshot, monto_final_bono) se almacenan cifrados
- El cifrado/des-cifrado se realiza en el Repository (capa de infraestructura)
- La clave de cifrado se gestiona vía Docker Secrets

AUDITORÍA:
- Tabla audit_logs registra todos los accesos a datos sensibles
- NO almacena los datos sensibles, solo metadatos de la operación
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    UUID,
    Numeric,
    String,
    Integer,
    DateTime,
    ForeignKey,
    func,
    LargeBinary,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class EvaluacionReadModel(Base):
    """
    Modelo de solo lectura para la tabla 'evaluaciones'.
    
    LFPDPPP: Principio de minimización - este servicio SOLO lee evaluaciones,
    nunca modifica ni elimina datos de esta tabla.
    
    Campos no sensibles: id, evaluado_id, evaluador_id, periodo_id, estado
    Campo potencialmente sensible: calificacion_global (no se considera
    dato personal sensible pero se trata con confidencialidad)
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
        Integer,
        nullable=False,
        comment="ID del periodo de evaluación"
    )
    estado: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        comment="Estado: DRAFT, SUBMITTED, APPROVED, REJECTED"
    )
    calificacion_global: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
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


class BonusModel(Base):
    """
    Modelo de escritura para la tabla 'bonos'.
    
    CUMPLIMIENTO:
    - LFPDPPP Art. 18-19: Cifrado en reposo para datos sensibles
    - OWASP Data Protection: encryption-at-rest para salarios y montos
    
    CAMPOS CIFRADOS (AES-256/Fernet - ver repository.py):
    - salario_base_snapshot: Salario del empleado al momento del cálculo
    - monto_final_bono: Monto final del bono calculado
    
    El cifrado/des-cifrado es transparente para el modelo.
    Los campos se almacenan como bytes cifrados en la BD.
    """
    __tablename__ = "bonos"
    __table_args__ = (
        Index("ix_bonos_evaluacion_id", "evaluacion_id"),
        Index("ix_bonos_fecha_calculo", "fecha_calculo"),
        Index("ix_bonos_calculado_por", "calculado_por"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID único del bono calculado"
    )

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluaciones.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK a evaluaciones.id"
    )

    salario_base_snapshot: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="CIFRADO Fernet(AES-256) - Salario base al momento del cálculo"
    )

    impacto_ebitda_logrado: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="% EBITDA corporativo logrado (0.00 - 999.99)"
    )

    performance_index: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Índice de rendimiento calculado (0.00 - 1.00)"
    )

    monto_final_bono: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="CIFRADO Fernet(AES-256) - Monto final del bono"
    )

    fecha_calculo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha y hora del cálculo"
    )

    calculado_por: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="user_id del token - Trazabilidad LFPDPPP Art. 21"
    )

    def __repr__(self) -> str:
        return f"<BonusModel id={self.id} evaluacion={self.evaluacion_id}>"


class AuditLogModel(Base):
    """
    Modelo de auditoría para cumplimiento LFPDPPP Art. 18-19 y 21.
    
    Registra TODOS los accesos y operaciones realizadas sobre datos sensibles.
    
    CUMPLIMIENTO:
    - LFPDPPP Art. 21: Registro de tratamientos (quién accedió a qué)
    - OWASP A09: Security Logging and Monitoring
    - OWASP A10: Server-Side Request Forgery prevention (logged)
    
    IMPORTANTE: Este modelo NO almacena datos sensibles.
    Solo registra metadatos: quién hizo qué, cuándo y desde dónde.
    
    DATOS SENSIBLES NUNCA REGISTRADOS:
    - salarios, montos de bono, calificaciones
    - tokens, passwords, claves de cifrado
    
    Se registran:
    - user_id (anonimizable si es necesario)
    - action: calculate_bonus, batch_calculate, report_access, etc.
    - resource_id: IDs de recursos afectados (evaluacion_id, periodo_id)
    - status: success, failure, blocked
    - detail: descripción genérica SIN datos sensibles
    - client_ip: IP parcialmente anonimizada (solo 2 octetos IPv4)
    - created_at: timestamp de la operación
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_status", "status"),
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
        index=True,
        comment="ID del usuario que realizó la acción"
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de acción: calculate_bonus, batch_calculate, report_access, auth_attempt"
    )

    resource_id: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="ID del recurso afectado (evaluacion_id o periodo_id)"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Estado: success, failure, blocked, denied"
    )

    detail: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Descripción de la acción SIN datos sensibles"
    )

    client_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=True,
        comment="IP del cliente anonimizada (ej: 192.168.***.***)"
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


class AuthenticationAttemptModel(Base):
    """
    Modelo para registrar intentos de autenticación.
    
    CUMPLIMIENTO:
    - OWASP Secure-by-Design: Registro de intentos fallidos
    - LFPDPPP Art. 18: Monitoreo de accesos
    
    Usado para detectar ataques de fuerza bruta.
    """
    __tablename__ = "auth_attempts"
    __table_args__ = (
        Index("ix_auth_attempts_ip", "ip_address"),
        Index("ix_auth_attempts_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="IP del cliente anonimizada"
    )

    success: Mapped[bool] = mapped_column(
        nullable=False,
        comment="True si el intento fue exitoso"
    )

    failure_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Razón del fallo (sin datos sensibles)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )