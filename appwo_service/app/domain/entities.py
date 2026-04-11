# app/domain/entities.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

# Importamos nuestras excepciones puras de dominio
from app.domain.exceptions import (
    InvalidTransitionException,
    UnauthorizedApprovalException,
    MissingJustificationException
)

# ==========================================
# Enums de Dominio (Tipos Fuertes)
# ==========================================

class EvaluationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

class ActorRole(str, Enum):
    COORDINATOR = "COORDINATOR"
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"
    ADMIN = "ADMIN"

# ==========================================
# Entidades (Value Objects y Aggregates)
# ==========================================

@dataclass(frozen=True)
class ApprovalSignature:
    """
    Value Object que representa la firma electrónica simple del evaluador.
    Es inmutable (frozen=True): una vez firmada, no se puede alterar en memoria.
    """
    actor_id: str
    actor_role: ActorRole
    signed_at: datetime
    signature_data: str  # Hash o string en Base64 proveniente del canvas del frontend
    ip_address: str


@dataclass(kw_only=True)
class EvaluationWorkflowEntity:
    """
    Entidad Central (Aggregate Root) del microservicio.
    Representa el estado actual de una evaluación en el flujo de firmas
    e implementa la Máquina de Estados para garantizar las reglas de negocio.
    """
    id: str  # UUID del flujo
    evaluation_id: str  # ID de la evaluación en el sistema de Django
    status: EvaluationStatus = EvaluationStatus.DRAFT
    requires_manager: bool = True
    justification_notes: Optional[str] = None
    
    # Lista de firmas recolectadas
    signatures: List[ApprovalSignature] = field(default_factory=list)
    
    created_at: datetime
    updated_at: datetime

    def has_manager_signature(self) -> bool:
        """Verifica si el Gerente ya estampó su firma."""
        return any(sig.actor_role == ActorRole.MANAGER for sig in self.signatures)

    def has_director_signature(self) -> bool:
        """Verifica si el Director ya estampó su firma."""
        return any(sig.actor_role == ActorRole.DIRECTOR for sig in self.signatures)
        
    def add_signature(self, signature: ApprovalSignature) -> None:
        """Agrega una firma a la lista."""
        self.signatures.append(signature)
        
    def clear_signatures(self) -> None:
        """Limpia las firmas (útil cuando se rechaza el flujo y debe volver a empezar)."""
        self.signatures.clear()

    # ==========================================
    # LÓGICA DE LA MÁQUINA DE ESTADOS (STATE MACHINE)
    # ==========================================

    def approve(self, actor_role: ActorRole) -> None:
        """
        Intenta aprobar el flujo actual basándose en el rol.
        Lanza excepciones de dominio si se viola la jerarquía.
        """
        if self.status != EvaluationStatus.PENDING_APPROVAL:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en PENDING_APPROVAL pueden ser aprobadas. Actual: {self.status}"
            )

        if actor_role == ActorRole.MANAGER:
            if not self.requires_manager:
                raise UnauthorizedApprovalException("Esta evaluación no requiere aprobación gerencial.")
            if self.has_manager_signature():
                raise InvalidTransitionException("El Gerente ya ha firmado esta evaluación.")
            
            # Nota: El estado se mantiene en PENDING_APPROVAL porque falta la firma del Director.

        elif actor_role == ActorRole.DIRECTOR:
            if self.requires_manager and not self.has_manager_signature():
                raise InvalidTransitionException("El Gerente debe aprobar antes que el Director.")
            if self.has_director_signature():
                raise InvalidTransitionException("El Director ya ha firmado esta evaluación.")
            
            # Al firmar el Director (después del Gerente, si aplicaba), la evaluación se aprueba.
            self.status = EvaluationStatus.APPROVED

        else:
            raise UnauthorizedApprovalException(f"El rol {actor_role} no tiene permisos para aprobar.")

    def reject(self, actor_role: ActorRole, justification: Optional[str]) -> None:
        """
        Rechaza el flujo, exigiendo justificación y limpiando firmas anteriores.
        """
        if self.status != EvaluationStatus.PENDING_APPROVAL:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en PENDING_APPROVAL pueden ser rechazadas. Actual: {self.status}"
            )
        
        if not justification or len(justification.strip()) == 0:
            raise MissingJustificationException("Es obligatorio proporcionar un comentario de justificación para el rechazo.")

        if actor_role not in (ActorRole.MANAGER, ActorRole.DIRECTOR):
            raise UnauthorizedApprovalException(f"El rol {actor_role} no tiene permisos para rechazar.")

        # El rechazo anula cualquier progreso previo
        self.status = EvaluationStatus.REJECTED
        self.clear_signatures()