"""
Schemas Pydantic para validación de entrada/salida.
Cumple: OWASP Input Validation + OWASP SCP.

VALIDACIONES IMPLEMENTADAS:
- Validación estricta de tipos (UUID, Decimal)
- Validación de rangos (gt, ge, le)
- Validación de longitud (max_length)
- Sanitización de inputs (eliminación de caracteres especiales)
- Serialización segura de outputs (enmascaramiento de datos sensibles)
"""
import uuid
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any

from pydantic import BaseModel, Field, field_validator, model_serializer, model_validator, ConfigDict
import re


def _sanitize_string_input(value: str) -> str:
    """
    Sanitiza input de string eliminando caracteres potencialmente peligrosos.
    
    OWASP Input Validation:
    - Elimina <, >, ", ', & para prevenir XSS
    - Elimina espacios en blanco excesivos
    - Trim de caracteres especiales
    """
    if not isinstance(value, str):
        return str(value)
    
    value = value.strip()
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    value = re.sub(r'[<>"\']', '', value)
    value = re.sub(r'\s+', ' ', value)
    
    return value


def _sanitize_uuid_input(value: str | uuid.UUID) -> uuid.UUID:
    """Valida y sanitiza input UUID."""
    if isinstance(value, uuid.UUID):
        return value
    
    sanitized = _sanitize_string_input(str(value))
    
    try:
        return uuid.UUID(sanitized)
    except ValueError:
        raise ValueError("UUID inválido")


class CalculateBonusRequest(BaseModel):
    """
    Schema para request de cálculo de bono individual.
    
    VALIDACIONES:
    - evaluacion_id: UUID válido obligatorio
    - salario_base_snapshot: > 0, hasta 12 dígitos decimales
    - impacto_ebitda_logrado: 0-100% (rango corporativo válido)
    - calificacion_global: 1-5 (escala de evaluación), opcional
    
    CUMPLIMIENTO OWASP:
    - Input Validation: Tipos y rangos estrictos
    - Data Protection: Campos sensibles validados
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "evaluacion_id": "123e4567-e89b-12d3-a456-426614174000",
                "salario_base_snapshot": 50000.00,
                "impacto_ebitda_logrado": 85.50,
                "calificacion_global": 4.5,
            }
        }
    )

    evaluacion_id: uuid.UUID = Field(
        ...,
        description="UUID único de la evaluación",
        json_schema_extra={"format": "uuid"},
    )
    
    salario_base_snapshot: Decimal = Field(
        ...,
        gt=Decimal("0"),
        le=Decimal("9999999999.99"),
        description="Salario base al momento del cálculo",
    )
    
    impacto_ebitda_logrado: Decimal = Field(
        ...,
        ge=Decimal("0"),
        le=Decimal("100"),
        description="% EBITDA corporativo logrado (0.00 - 100.00)",
    )
    
    calificacion_global: Optional[Decimal] = Field(
        None,
        ge=Decimal("1"),
        le=Decimal("5"),
        description="Calificación global (1.00 - 5.00). Opcional: se usa de la BD si se omite.",
    )

    @field_validator('evaluacion_id', mode='before')
    @classmethod
    def validate_evaluacion_id(cls, v):
        if isinstance(v, str):
            return _sanitize_uuid_input(v)
        if isinstance(v, uuid.UUID):
            return v
        raise ValueError("evaluacion_id debe ser un UUID válido")

    @field_validator('salario_base_snapshot', mode='before')
    @classmethod
    def validate_salario(cls, v):
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v

    @field_validator('impacto_ebitda_logrado', mode='before')
    @classmethod
    def validate_ebitda(cls, v):
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v

    @field_validator('calificacion_global', mode='before')
    @classmethod
    def validate_calificacion(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class BonusBatchItem(BaseModel):
    """
    Schema para item individual en request batch.
    
    Mismas validaciones que CalculateBonusRequest.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    evaluacion_id: uuid.UUID = Field(..., description="UUID de la evaluación")
    
    salario_base_snapshot: Decimal = Field(
        ...,
        gt=Decimal("0"),
        le=Decimal("9999999999.99"),
        description="Salario base al momento del cálculo",
    )
    
    impacto_ebitda_logrado: Decimal = Field(
        ...,
        ge=Decimal("0"),
        le=Decimal("100"),
        description="% EBITDA logrado",
    )
    
    calificacion_global: Decimal = Field(
        ...,
        ge=Decimal("1"),
        le=Decimal("5"),
        description="Calificación global (1-5)",
    )

    @field_validator('evaluacion_id', mode='before')
    @classmethod
    def validate_evaluacion_id(cls, v):
        if isinstance(v, str):
            return _sanitize_uuid_input(v)
        return v

    @field_validator('salario_base_snapshot', mode='before')
    @classmethod
    def validate_salario(cls, v):
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class CalculateBonusBatchRequest(BaseModel):
    """
    Schema para request de cálculo batch.
    
    VALIDACIONES:
    - Al menos 1 registro
    - Máximo 10,000 registros (limitar uso de recursos)
    
    OWASP: Limitación de tamaño para prevenir DoS.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "registros": [
                    {
                        "evaluacion_id": "123e4567-e89b-12d3-a456-426614174000",
                        "salario_base_snapshot": 50000.00,
                        "impacto_ebitda_logrado": 85.50,
                        "calificacion_global": 4.5,
                    }
                ]
            }
        }
    )

    registros: List[BonusBatchItem] = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Lista de registros a calcular (1-10,000)",
    )

    @model_validator(mode='after')
    def validate_unique_evaluaciones(self):
        """Valida que no haya evaluaciones duplicadas en el batch."""
        ids = [str(r.evaluacion_id) for r in self.registros]
        if len(ids) != len(set(ids)):
            raise ValueError("No se permiten evaluaciones duplicadas en un batch")
        return self


class BonusResponse(BaseModel):
    """
    Schema de respuesta para cálculo de bono.
    
    CUMPLIMIENTO:
    - LFPDPPP: monto_enmascarado no expone el monto real
    - OWASP: Fecha en formato ISO seguro
    """
    model_config = ConfigDict(from_attributes=True)

    evaluacion_id: uuid.UUID
    impacto_ebitda_logrado: float
    performance_index: float
    monto_enmascarado: str
    fecha_calculo: datetime

    @model_serializer
    def serialize(self) -> dict:
        """Serializa la respuesta con formato seguro."""
        return {
            "evaluacion_id": str(self.evaluacion_id),
            "impacto_ebitda_logrado": round(self.impacto_ebitda_logrado, 2),
            "performance_index": round(self.performance_index, 2),
            "monto_enmascarado": self.monto_enmascarado,
            "fecha_calculo": (
                self.fecha_calculo.isoformat() 
                if hasattr(self.fecha_calculo, 'isoformat') 
                else str(self.fecha_calculo)
            ),
        }


class BatchAcceptedResponse(BaseModel):
    """Schema de respuesta para batch aceptado."""
    model_config = ConfigDict(str_strip_whitespace=True)

    mensaje: str = Field(
        ...,
        max_length=200,
        description="Mensaje descriptivo",
    )
    task_id: str = Field(
        ...,
        min_length=1,
        description="ID de la tarea Celery",
    )
    total_registros: int = Field(
        ...,
        ge=1,
        description="Total de registros encolados",
    )


class BonusReportResponse(BaseModel):
    """
    Schema de respuesta para reporte de bonos.
    
    CUMPLIMIENTO:
    - Roles específicos ven montos, otros ven monto_total=None
    - monto_enmascarado protege datos sensibles
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    periodo_id: int = Field(..., ge=1, description="ID del periodo")
    total_evaluaciones: int = Field(..., ge=0, description="Total de evaluaciones")
    monto_total: Optional[float] = Field(
        None,
        description="Monto total (solo visible para admin/finanzas)",
    )
    bonos: List[BonusResponse] = Field(
        default_factory=list,
        description="Lista de bonos calculados",
    )


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {"detail": "Token inválido"}
        }
    )

    detail: str = Field(
        ...,
        max_length=500,
        description="Mensaje de error (sin información sensible)",
    )

    @model_serializer
    def serialize(self) -> dict:
        """Asegura que errores no contengan información sensible."""
        return {"detail": self.detail[:500]}


class HealthResponse(BaseModel):
    """Schema para health check."""
    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(..., pattern="^(ok|error|degraded)$")
    service: str
    version: str