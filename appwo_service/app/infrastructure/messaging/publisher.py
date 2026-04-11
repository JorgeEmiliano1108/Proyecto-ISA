# app/infrastructure/messaging/publisher.py
import json
import redis.asyncio as redis
from app.application.ports.output import IEventPublisher
from app.domain.entities import EvaluationWorkflowEntity

class RedisEventPublisher(IEventPublisher):
    """
    Adaptador de mensajería usando Redis Pub/Sub o Streams.
    """
    def __init__(self, redis_url: str):
        # decode_responses=True decodifica los bytes a string automáticamente
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    async def publish_workflow_event(self, event_type: str, workflow: EvaluationWorkflowEntity, actor_id: str) -> None:
        """
        Empaqueta la entidad en un JSON seguro y lo publica en la cola.
        """
        payload = {
            "event_type": event_type,  # Ej. "EVALUATION_APPROVED" o "EVALUATION_REJECTED"
            "workflow_id": str(workflow.id),
            "evaluation_id": workflow.evaluation_id,
            "new_status": workflow.status.value,
            "actor_id": actor_id,
            "timestamp": workflow.updated_at.isoformat()
        }
        
        # Publicamos en el canal 'approval_events'
        await self.redis_client.publish("approval_events", json.dumps(payload))
        
        # Opcional (Log de sistema para monitoreo de contenedores)
        print(f"[EVENT BUS] Evento '{event_type}' publicado para evaluación {workflow.evaluation_id}")