# app/domain/entities.py
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator, IPvAnyAddress

from .exceptions import InvalidAuditLogActionException

# Lista de acciones controladas (Business Rules)
# Todo lo que no esté aquí, será rechazado por el dominio.
PERMITTED_ACTIONS = {
    "CREATE_EVALUATION",
    "UPDATE_DRAFT",
    "STATE_TRANSITION",
    "ASSIGN_BONUS",
    "EXPORT_REPORT",
    "SYSTEM_ADMIN_OVERRIDE"
}

class AuditLog(BaseModel):
    """
    Entidad Central del Dominio: Representa un registro de auditoría inmutable.
    Cumple con LFPDPPP: Trazabilidad completa (Quién, Qué, Dónde, Cuándo, Por Qué).
    """
    
    # model_config asegura el strict mode y hace la instancia inmutable en memoria (frozen=True)
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    actor_id: UUID = Field(..., description="ID del usuario o sistema que realizó la acción")
    action: str = Field(..., min_length=3, max_length=50)
    resource_id: Optional[UUID] = Field(None, description="ID del recurso afectado (ej. Evaluación)")
    resource_type: str = Field(..., min_length=2, max_length=50, description="Ej: 'EvaluationWorkflow'")
    ip_address: IPvAnyAddress = Field(..., description="Origen de la petición para trazabilidad")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Details almacena el diff (pre/post) o justificaciones. 
    # DEBE estar sanitizado antes de llegar aquí (responsabilidad del Caso de Uso).
    details: Dict[str, Any] = Field(default_factory=dict)
    
    # La firma criptográfica HMAC (Tamper-Evidence). Es opcional en la creación, 
    # pero el caso de uso la llenará usando el método 'with_signature'.
    signature: Optional[str] = Field(default=None)

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Regla de Negocio: Solo permitimos acciones registradas en el diccionario."""
        action_upper = v.upper()
        if action_upper not in PERMITTED_ACTIONS:
            raise InvalidAuditLogActionException(action=v)
        return action_upper

    @field_validator("timestamp")
    @classmethod
    def validate_timezone(cls, v: datetime) -> datetime:
        """Regla de Negocio: Todo log debe estar en UTC para evitar desincronizaciones."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    def with_signature(self, signature: str) -> "AuditLog":
        """
        Dado que la entidad es inmutable (frozen=True), no podemos hacer `self.signature = signature`.
        Devolvemos una nueva instancia idéntica pero con la firma aplicada.
        """
        return self.model_copy(update={"signature": signature})

    def to_dict_for_signing(self) -> Dict[str, Any]:
        """
        Extrae un diccionario determinista con los campos exactos que deben ser 
        protegidos por el hash HMAC. Excluimos el 'id' si este se genera en BD y la propia 'signature'.
        """
        return {
            "actor_id": str(self.actor_id),
            "action": self.action,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "resource_type": self.resource_type,
            "ip_address": str(self.ip_address),
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }