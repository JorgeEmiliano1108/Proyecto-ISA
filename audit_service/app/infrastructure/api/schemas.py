# app/infrastructure/api/schemas.py
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress

class AuditLogCreateRequest(BaseModel):
    """
    Payload esperado cuando un microservicio quiere registrar un evento.
    El actor_id y la ip_address no se piden aquí, se extraen del token JWT 
    y de los headers HTTP por seguridad.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    action: str = Field(..., min_length=3, max_length=50, example="STATE_TRANSITION")
    resource_id: Optional[UUID] = Field(None, description="ID del recurso afectado")
    resource_type: str = Field(..., min_length=2, max_length=50, example="EvaluationWorkflow")
    details: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Payload pre/post o comentarios. Será sanitizado en el backend."
    )

class AuditLogResponse(BaseModel):
    """
    Respuesta de la API al consultar logs.
    """
    model_config = ConfigDict(from_attributes=True) # Permite leer de las Entidades de Dominio

    id: UUID
    actor_id: UUID
    action: str
    resource_id: Optional[UUID]
    resource_type: str
    ip_address: IPvAnyAddress
    timestamp: datetime
    details: Dict[str, Any]
    signature: str # Exportamos la firma por si el cliente quiere verificar la inmutabilidad