# app/application/use_cases/start_review.py
from app.domain.exceptions import DomainException
from app.application.ports.output import IApprovalRepository, IEventPublisher, IUserServiceClient

class StartReviewUseCase:
    """
    Caso de uso para que un rol autorizado tome una evaluación en estado RECIBIDO
    y comience a revisarla, moviéndola a EN_REVISION.
    """
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
        ip_address: str
    ) -> dict:
        
        # 1. Recuperar la entidad
        workflow = await self.repository.get_workflow_by_eval_id(evaluation_id)
        if not workflow:
            raise DomainException(f"No se encontró el flujo para la evaluación {evaluation_id}")

        # 2. Consultar el rol del actor
        actor_role = await self.user_service.get_actor_role(actor_id)

        # 3. DELEGAR AL DOMINIO: Iniciar revisión
        workflow.start_review(actor_role)

        # 4. Persistencia
        await self.repository.save_workflow(workflow)

        # 5. Publicar evento
        await self.event_publisher.publish_workflow_event(
            event_type="EVALUATION_UNDER_REVIEW",
            workflow=workflow,
            actor_id=actor_id
        )

        return {
            "status": "success",
            "current_workflow_status": workflow.status,
            "message": "La evaluación ha pasado a estado EN_REVISION."
        }
