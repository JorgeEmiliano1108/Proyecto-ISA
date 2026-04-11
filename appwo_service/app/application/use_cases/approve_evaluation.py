# app/application/use_cases/approve_evaluation.py
from datetime import datetime, timezone
from app.domain.entities import ApprovalSignature
from app.domain.exceptions import DomainException, MissingSignatureException
from app.application.ports.output import IApprovalRepository, IEventPublisher, IUserServiceClient

class ApproveEvaluationUseCase:
    """
    Orquesta el flujo de aprobación de una evaluación.
    Inyectamos las dependencias por el constructor para facilitar el Testing.
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
        signature_data: str, 
        ip_address: str
    ) -> dict:
        
        # Validar que la firma (canvas) no venga vacía
        if not signature_data or len(signature_data.strip()) == 0:
            raise MissingSignatureException("La firma electrónica es obligatoria para aprobar.")

        # Recuperar la entidad del repositorio
        workflow = await self.repository.get_workflow_by_eval_id(evaluation_id)
        if not workflow:
            raise DomainException(f"No se encontró el flujo para la evaluación {evaluation_id}")

        # Consultar el rol del actor (Comunicación entre microservicios)
        actor_role = await self.user_service.get_actor_role(actor_id)

        # DELEGAR AL DOMINIO: Ejecutar las reglas de negocio estrictas
        # Si el rol no corresponde o el estado no es el correcto, el dominio lanzará una excepción.
        workflow.approve(actor_role)

        # 5. Si el dominio aprueba, creamos el Value Object de la firma (Inmutable)
        signature = ApprovalSignature(
            actor_id=actor_id,
            actor_role=actor_role,
            signed_at=datetime.now(timezone.utc),
            signature_data=signature_data,
            ip_address=ip_address
        )
        
        # Adjuntamos la firma a la entidad
        workflow.add_signature(signature)

        # 6. Guardar los cambios (Transacción ACID en el repositorio)
        await self.repository.save_workflow(workflow)

        # 7. Disparar el evento asíncrono para el Audit Service y notificaciones
        await self.event_publisher.publish_workflow_event(
            event_type="EVALUATION_APPROVED",
            workflow=workflow,
            actor_id=actor_id
        )

        return {
            "status": "success",
            "current_workflow_status": workflow.status,
            "message": "Evaluación aprobada y firmada exitosamente."
        }