# app/application/use_cases/reject_evaluation.py
from app.domain.exceptions import DomainException
from app.application.ports.output import IApprovalRepository, IEventPublisher, IUserServiceClient

class RejectEvaluationUseCase:
    def __init__(
        self,
        repository: IApprovalRepository,
        event_publisher: IEventPublisher,
        user_service: IUserServiceClient
    ):
        self.repository = repository
        self.event_publisher = event_publisher
        self.user_service = user_service

    async def execute(
        self, 
        evaluation_id: str, 
        actor_id: str, 
        justification: str,
        ip_address: str
    ) -> dict:
        
        # 1. Recuperar la entidad
        workflow = await self.repository.get_workflow_by_eval_id(evaluation_id)
        if not workflow:
            raise DomainException(f"No se encontró el flujo para la evaluación {evaluation_id}")

        # 2. Consultar el rol del actor
        actor_role = await self.user_service.get_actor_role(actor_id)

        # 3. DELEGAR AL DOMINIO: Intento de rechazo
        # Aquí el dominio valida obligatoriamente la existencia de 'justification'
        workflow.reject(actor_role, justification)

        # 4. Actualizar la entidad con la justificación y limpiar firmas anuladas
        workflow.justification_notes = justification
        workflow.clear_signatures()

        # 5. Persistencia
        await self.repository.save_workflow(workflow)

        # 6. Publicar evento (Para que el Audit Service analice el rechazo con IA)
        await self.event_publisher.publish_workflow_event(
            event_type="EVALUATION_REJECTED",
            workflow=workflow,
            actor_id=actor_id
        )

        return {
            "status": "success",
            "current_workflow_status": workflow.status,
            "message": "La evaluación ha sido rechazada y regresada a DRAFT."
        }