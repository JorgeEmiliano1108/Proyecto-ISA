# app/infrastructure/database/repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.ports.output import IApprovalRepository
from app.domain.entities import EvaluationWorkflowEntity, ApprovalSignature
from app.infrastructure.database.models import WorkflowModel, SignatureModel

class ApprovalRepository(IApprovalRepository):
    """
    Adaptador de Persistencia. 
    Traduce entre la BD (SQLAlchemy) y la RAM (Entities).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workflow_by_eval_id(self, evaluation_id: str) -> Optional[EvaluationWorkflowEntity]:
        # Consultamos el flujo y hacemos un JOIN adelantado (selectinload) de las firmas
        stmt = select(WorkflowModel).options(selectinload(WorkflowModel.signatures)).where(WorkflowModel.evaluation_id == evaluation_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Mapear las firmas (Model -> Value Object)
        signatures_entities = [
            ApprovalSignature(
                actor_id=sig.actor_id,
                actor_role=sig.actor_role,
                signed_at=sig.signed_at,
                signature_data=sig.signature_data,
                ip_address=sig.ip_address
            ) for sig in model.signatures
        ]

        # Mapear el flujo (Model -> Aggregate Root)
        return EvaluationWorkflowEntity(
            id=str(model.id),
            evaluation_id=model.evaluation_id,
            status=model.status,
            requires_manager=model.requires_manager,
            justification_notes=model.justification_notes,
            signatures=signatures_entities,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def save_workflow(self, workflow: EvaluationWorkflowEntity) -> None:
        # Recuperamos el modelo de base de datos para actualizarlo
        stmt = select(WorkflowModel).options(selectinload(WorkflowModel.signatures)).where(WorkflowModel.id == workflow.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            # Lógica de inserción (si fuera un registro nuevo)
            pass 
        else:
            # 1. Actualizar campos base
            model.status = workflow.status
            model.justification_notes = workflow.justification_notes
            model.updated_at = workflow.updated_at

            # 2. Sincronizar firmas (Si el dominio limpió las firmas por un rechazo, las borramos de BD)
            if len(workflow.signatures) == 0:
                model.signatures = [] # El 'delete-orphan' de SQLAlchemy se encarga de borrarlas físicamente
            else:
                # Si hay nuevas firmas en memoria que no están en DB, las insertamos
                existing_data = [s.signature_data for s in model.signatures]
                for sig in workflow.signatures:
                    if sig.signature_data not in existing_data:
                        new_sig_model = SignatureModel(
                            actor_id=sig.actor_id,
                            actor_role=sig.actor_role,
                            signed_at=sig.signed_at,
                            signature_data=sig.signature_data,
                            ip_address=sig.ip_address
                        )
                        model.signatures.append(new_sig_model)

            self.session.add(model)
            await self.session.commit()