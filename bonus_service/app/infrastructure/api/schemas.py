"""
Schemas Pydantic para validación de entrada/salida.
Cumple: OWASP Input Validation + OWASP SCP.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class CalculoLogroRequest(BaseModel):
    """
    Schema para request de cálculo de logro individual.

    VALIDACIONES OWASP:
    - evaluacion_id: UUID válido obligatorio
    - calificacion_global: estrictamente entre 1.0 y 5.0
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    evaluacion_id: uuid.UUID = Field(
        ...,
        description="UUID único de la evaluación",
        json_schema_extra={"format": "uuid"},
    )

    calificacion_global: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Calificación global del evaluador (1.0 - 5.0)",
    )

    @field_validator('evaluacion_id', mode='before')
    @classmethod
    def validate_evaluacion_id(cls, v):
        if isinstance(v, str):
            try:
                return uuid.UUID(v)
            except ValueError:
                raise ValueError("evaluacion_id debe ser un UUID válido")
        if isinstance(v, uuid.UUID):
            return v
        raise ValueError("evaluacion_id debe ser un UUID válido")


class CalculoLogroBatchItem(BaseModel):
    """Schema para item individual en request batch."""
    model_config = ConfigDict(str_strip_whitespace=True)

    evaluacion_id: uuid.UUID = Field(..., description="UUID de la evaluación")
    calificacion_global: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Calificación global (1.0 - 5.0)",
    )

    @field_validator('evaluacion_id', mode='before')
    @classmethod
    def validate_evaluacion_id(cls, v):
        if isinstance(v, str):
            try:
                return uuid.UUID(v)
            except ValueError:
                raise ValueError("evaluacion_id debe ser un UUID válido")
        if isinstance(v, uuid.UUID):
            return v
        raise ValueError("evaluacion_id debe ser un UUID válido")


class CalculoLogroBatchRequest(BaseModel):
    """
    Schema para request de cálculo batch.
    OWASP: Limitación de tamaño para prevenir DoS.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    registros: List[CalculoLogroBatchItem] = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Lista de registros a calcular (1-10,000)",
    )


class CalculoLogroResponse(BaseModel):
    """Schema de respuesta para cálculo de logro."""
    model_config = ConfigDict(from_attributes=True)

    evaluacion_id: uuid.UUID
    calificacion_global: float
    porcentaje_logro: float
    fecha_calculo: datetime


class CalculoLogroReportResponse(BaseModel):
    """Schema de respuesta para reporte de logros."""
    model_config = ConfigDict(str_strip_whitespace=True)

    periodo_id: int = Field(..., ge=1, description="ID del periodo")
    total_evaluaciones: int = Field(..., ge=0, description="Total de evaluaciones")
    calculos: List[CalculoLogroResponse] = Field(
        default_factory=list,
        description="Lista de cálculos de logro",
    )


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


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"example": {"detail": "Token inválido"}}
    )

    detail: str = Field(
        ...,
        max_length=500,
        description="Mensaje de error (sin información sensible)",
    )


class LoginRequest(BaseModel):
    """
    Schema para request de login de prueba.
    
    ⚠️ SOLO PARA DESARROLLO - NO USAR EN PRODUCCIÓN
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Nombre de usuario (para logging)",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contraseña (para logging)",
    )


class LoginResponse(BaseModel):
    """
    Schema para respuesta de login.
    
    ⚠️ SOLO PARA DESARROLLO - NO USAR EN PRODUCCIÓN
    """
    access_token: str = Field(..., description="Token JWT válido")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    roles: List[str] = Field(..., description="Roles del usuario")


class CalculoLogroListItem(BaseModel):
    """Schema para item de lista de cálculos de logro."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    calificacion_global: float
    porcentaje_logro: float
    fecha_calculo: datetime
    calculado_por: str


class PaginatedCalculosResponse(BaseModel):
    """Schema de respuesta paginada para listado de cálculos."""
    model_config = ConfigDict(str_strip_whitespace=True)

    total: int = Field(..., ge=0, description="Total de registros")
    page: int = Field(..., ge=1, description="Página actual")
    page_size: int = Field(..., ge=1, le=100, description="Tamaño de página")
    total_pages: int = Field(..., ge=0, description="Total de páginas")
    items: List[CalculoLogroListItem] = Field(default_factory=list, description="Lista de cálculos")


class CalculosListQueryParams(BaseModel):
    """Query parameters para listar cálculos con filtros."""
    model_config = ConfigDict(str_strip_whitespace=True)

    evaluacion_id: Optional[uuid.UUID] = Field(None, description="Filtrar por evaluación")
    calculado_por: Optional[str] = Field(None, description="Filtrar por usuario que calculó")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde (inclusive)")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta (inclusive)")
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(20, ge=1, le=100, description="Tamaño de página")
