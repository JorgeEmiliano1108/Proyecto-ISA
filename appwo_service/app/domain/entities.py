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
    RECIBIDO = "RECIBIDO"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    NO_APROBADO = "NO_APROBADO"

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
    status: EvaluationStatus = EvaluationStatus.RECIBIDO
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

    def start_review(self, actor_role: ActorRole) -> None:
        """Inicia la revisión: RECIBIDO → EN_REVISION.
        Solo roles autorizados (MANAGER) pueden iniciar la revisión.
        """
        if self.status != EvaluationStatus.RECIBIDO:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en RECIBIDO pueden pasar a EN_REVISION. Actual: {self.status}"
            )
        if actor_role != ActorRole.MANAGER:
            raise UnauthorizedApprovalException(f"El rol {actor_role} no está autorizado para iniciar la revisión.")
        self.status = EvaluationStatus.EN_REVISION

    # ==========================================
    # LÓGICA DE LA MÁQUINA DE ESTADOS (STATE MACHINE)
    # ==========================================

    def approve(self, actor_role: ActorRole) -> None:
        """
        Aprobar la evaluación cuando está en EN_REVISION.
        Solo roles con permiso pueden aprobar y el estado resultante es APROBADO.
        """
        if self.status != EvaluationStatus.EN_REVISION:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en EN_REVISION pueden ser aprobadas. Actual: {self.status}"
            )

        # En este flujo simplificado, cualquier rol autorizado (MANAGER o DIRECTOR) puede aprobar directamente.
        if actor_role not in (ActorRole.MANAGER, ActorRole.DIRECTOR):
            raise UnauthorizedApprovalException(f"El rol {actor_role} no tiene permisos para aprobar.")

        # No se manejan firmas adicionales aquí; simplemente cambiamos el estado.
        self.status = EvaluationStatus.APROBADO


    def reject(self, actor_role: ActorRole, justification: Optional[str]) -> None:
        """
        Rechaza la evaluación cuando está EN_REVISION.
        Requiere justificación y cambia el estado a NO_APROBADO.
        """
        if self.status != EvaluationStatus.EN_REVISION:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en EN_REVISION pueden ser rechazadas. Actual: {self.status}"
            )
        
        if not justification or len(justification.strip()) == 0:
            raise MissingJustificationException("Es obligatorio proporcionar un comentario de justificación para el rechazo.")

        if actor_role not in (ActorRole.MANAGER, ActorRole.DIRECTOR):
            raise UnauthorizedApprovalException(f"El rol {actor_role} no tiene permisos para rechazar.")

        # Cambiamos el estado y limpiamos firmas anteriores
        self.status = EvaluationStatus.NO_APROBADO
        self.clear_signatures()