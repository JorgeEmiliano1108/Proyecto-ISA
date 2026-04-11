# app/domain/state_machine.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional

# Enums de Dominio (Tipos Fuertes)

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


# Excepciones Puras de Negocio


class InvalidTransitionException(Exception):
    """Lanzada cuando se intenta un salto de estado no permitido."""
    pass

class UnauthorizedApprovalException(Exception):
    """Lanzada cuando un rol intenta aprobar fuera de su jerarquía."""
    pass

class MissingJustificationException(Exception):
    """Lanzada cuando se intenta rechazar sin proporcionar un motivo."""
    pass


# Entidad de Dominio / Máquina de Estados


@dataclass
class ApprovalWorkflow:
    """
    Máquina de estados finitos que gobierna el ciclo de vida de una evaluación.
    Garantiza el cumplimiento estricto de las reglas de negocio de ISA Corporativo.
    """
    evaluation_id: str
    status: EvaluationStatus
    requires_manager: bool
    manager_approved: bool = False
    director_approved: bool = False

    def submit(self) -> None:
        """
        Transición: DRAFT -> SUBMITTED
        El Coordinador envía la evaluación para revisión.
        """
        if self.status not in (EvaluationStatus.DRAFT, EvaluationStatus.REJECTED):
            raise InvalidTransitionException(f"No se puede enviar una evaluación en estado {self.status}")
        self.status = EvaluationStatus.SUBMITTED

    def start_approval_process(self) -> None:
        """
        Transición: SUBMITTED -> PENDING_APPROVAL
        El sistema inicia formalmente la etapa de recolección de firmas.
        """
        if self.status != EvaluationStatus.SUBMITTED:
            raise InvalidTransitionException(f"La evaluación debe estar SUBMITTED para iniciar aprobación. Actual: {self.status}")
        self.status = EvaluationStatus.PENDING_APPROVAL

    def approve(self, actor_role: ActorRole) -> None:
        """
        Transición interna y final hacia APPROVED.
        Aplica las reglas de jerarquía multinivel.
        """
        if self.status != EvaluationStatus.PENDING_APPROVAL:
            raise InvalidTransitionException(
                f"Solo las evaluaciones en PENDING_APPROVAL pueden ser aprobadas. Actual: {self.status}"
            )

        if actor_role == ActorRole.MANAGER:
            if not self.requires_manager:
                raise UnauthorizedApprovalException("Esta evaluación no requiere aprobación gerencial.")
            if self.manager_approved:
                raise InvalidTransitionException("El Gerente ya ha firmado esta evaluación.")
            
            self.manager_approved = True
            # Nota: El estado se mantiene en PENDING_APPROVAL porque falta el Director.

        elif actor_role == ActorRole.DIRECTOR:
            if self.requires_manager and not self.manager_approved:
                raise InvalidTransitionException("El Gerente debe aprobar antes que el Director.")
            if self.director_approved:
                raise InvalidTransitionException("El Director ya ha firmado esta evaluación.")
            
            self.director_approved = True
            # Al firmar el Director, la evaluación está oficialmente aprobada.
            self.status = EvaluationStatus.APPROVED

        else:
            raise UnauthorizedApprovalException(f"El rol {actor_role} no tiene permisos para aprobar.")

    def reject(self, actor_role: ActorRole, justification: Optional[str]) -> None:
        """
        Transición: PENDING_APPROVAL -> REJECTED
        Exige justificación obligatoria. Rompe las firmas previas.
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
        self.manager_approved = False
        self.director_approved = False

    def reset_to_draft(self) -> None:
        """
        Transición: REJECTED -> DRAFT
        Permite al Coordinador volver a editar tras un rechazo.
        """
        if self.status != EvaluationStatus.REJECTED:
            raise InvalidTransitionException(f"Solo una evaluación REJECTED puede regresar a DRAFT. Actual: {self.status}")
        self.status = EvaluationStatus.DRAFT

    def close_evaluation(self) -> None:
        """
        Transición: APPROVED -> CLOSED
        Cierre definitivo del periodo fiscal/evaluativo.
        """
        if self.status != EvaluationStatus.APPROVED:
            raise InvalidTransitionException(f"Solo una evaluación APPROVED puede ser CLOSED. Actual: {self.status}")
        self.status = EvaluationStatus.CLOSED