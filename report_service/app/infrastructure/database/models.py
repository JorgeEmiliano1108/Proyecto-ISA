"""app/infrastructure/database/models.py
Mapeo Objeto-Relacional (ORM) de la base de datos de ISA Corporativo.
Representa fielmente el esquema SQL de evaluación y bonos.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, UUID, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.database import Base

# --- CATÁLOGOS ---

class RoleModel(Base):
    __tablename__ = "cat_roles"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    nivel_aprobacion = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)

class DepartamentoModel(Base):
    __tablename__ = "cat_departamentos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)

class CompetenciaModel(Base):
    __tablename__ = "cat_competencias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

# --- SEGURIDAD Y USUARIOS ---

class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(50), unique=True, nullable=False)
    rol_id = Column(Integer, ForeignKey("cat_roles.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("cat_departamentos.id"), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

# --- TRANSACCIONAL ---

class EvaluacionModel(Base):
    __tablename__ = "evaluaciones"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    evaluado_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    evaluador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    periodo_id = Column(Integer, nullable=False)
    estado = Column(String(50), default="DRAFT")
    logros_previos = Column(Text)
    comentarios_evaluador = Column(Text)
    comentarios_evaluado = Column(Text)
    calificacion_global = Column(DECIMAL(3, 2))
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

class CompetenciaDetalleModel(Base):
    __tablename__ = "competencias_detalle"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id", ondelete="CASCADE"), nullable=False)
    competencia_id = Column(Integer, ForeignKey("cat_competencias.id"), nullable=False)
    calificacion = Column(Integer)
    comentario = Column(Text, nullable=False)

# --- FINANZAS ---

class BonoModel(Base):
    __tablename__ = "bonos"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id", ondelete="CASCADE"), nullable=False)
    salario_base_snapshot = Column(DECIMAL(12, 2), nullable=False)
    impacto_ebitda_logrado = Column(DECIMAL(5, 2), nullable=False)
    performance_index = Column(DECIMAL(5, 2), nullable=False)
    monto_final_bono = Column(DECIMAL(12, 2), nullable=False)
    fecha_calculo = Column(DateTime(timezone=True), server_default=func.now())

# --- AUDITORÍA DE REPORTES (Específico de este Microservicio) ---

class ReportAuditModel(Base):
    __tablename__ = "isa_reports_audit"
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False) # STARTED, AVAILABLE, FAILED, DELETED
    result_url = Column(Text)
    error_message = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())