# app/domain/entities.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class EmpleadoBasico(BaseModel):
    model_config = ConfigDict(frozen=True) # Inmutable
    id: str
    username: str
    departamento: str
    rol: str

class CompetenciaEvaluada(BaseModel):
    model_config = ConfigDict(frozen=True)
    nombre: str
    calificacion: int
    comentario: str

class EvaluacionISA(BaseModel):
    """Representa todos los datos crudos extraídos de la BD antes de sanitizar."""
    model_config = ConfigDict(frozen=True)
    
    evaluacion_id: str
    evaluado: EmpleadoBasico
    evaluador: EmpleadoBasico
    estado: str
    calificacion_global: Optional[float]
    logros_previos: Optional[str]
    comentarios_evaluador: Optional[str]
    comentarios_evaluado: Optional[str]
    competencias: List[CompetenciaEvaluada]
    bono_asignado: Optional[float] = None
    fecha_creacion: datetime

class SanitizedReportData(BaseModel):
    """Representa los datos limpios y enmascarados, listos para enviar al LLM (Phi-3)."""
    model_config = ConfigDict(frozen=True)
    
    report_type: str
    profile_name: str
    institution_id: str
    safe_payload: Dict[str, Any] # Aquí van los datos de la evaluación ya enmascarados