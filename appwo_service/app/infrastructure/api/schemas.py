# app/infrastructure/api/schemas.py
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

# Requests (Entradas)

class ApproveEvaluationRequest(BaseModel):
    """Payload exigido cuando un gerente/director aprueba una evaluación."""
    # Uso moderno de Pydantic V2 con Annotated para evitar errores de Linter
    signature_data: Annotated[str, StringConstraints(min_length=10, strip_whitespace=True)] = Field(
        ..., 
        description="Firma electrónica generada en canvas (Base64 o Hash). No puede estar vacía."
    )

class RejectEvaluationRequest(BaseModel):
    """Payload exigido cuando se rechaza un flujo."""
    justification: Annotated[str, StringConstraints(min_length=5, max_length=500, strip_whitespace=True)] = Field(
        ..., 
        description="Motivo detallado del rechazo. Obligatorio."
    )

# Responses (Salidas)

class WorkflowActionResponse(BaseModel):
    """Contrato de respuesta estándar para la API."""
    status: str = Field(..., example="success")
    current_workflow_status: str = Field(..., example="APPROVED")
    message: str = Field(..., example="Evaluación aprobada y firmada exitosamente.")

class ErrorResponse(BaseModel):
    """Contrato estandarizado para ocultar detalles del servidor (OWASP)."""
    detail: str