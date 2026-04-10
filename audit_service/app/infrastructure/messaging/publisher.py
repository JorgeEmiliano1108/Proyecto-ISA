# app/infrastructure/messaging/publisher.py
import json
import logging
from redis.asyncio import Redis, ConnectionPool
from app.application.ports.output import EventPublisherPort
from app.domain.entities import AuditLog
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisEventPublisher(EventPublisherPort):
    """
    Adaptador de salida para publicar eventos asíncronos en Redis Pub/Sub o Streams.
    Cumple con el NFR de Resiliencia: Si Redis falla, captura el error para no 
    tumbar la transacción principal de PostgreSQL.
    """
    
    def __init__(self):
        # Usamos un ConnectionPool para eficiencia en concurrencia (FastAPI async)
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL, 
            decode_responses=True
        )
        self.redis = Redis(connection_pool=self.pool)

    async def publish_audit_event(self, event_name: str, log: AuditLog) -> None:
        try:
            # Preparamos el payload serializando la entidad inmutable
            # Convertimos UUIDs y datetimes a strings compatibles con JSON
            payload = {
                "event": event_name,
                "data": {
                    "id": str(log.id),
                    "actor_id": str(log.actor_id),
                    "action": log.action,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "resource_type": log.resource_type,
                    "timestamp": log.timestamp.isoformat(),
                    # Omitimos 'details' y 'signature' en el evento público por seguridad (Minimización LFPDPPP).
                    # Si la IA necesita los detalles, debe consultarlos vía API con credenciales.
                }
            }
            
            message = json.dumps(payload)
            
            # Publicamos en el canal (ej. canal: 'audit_events')
            await self.redis.publish("audit_events", message)
            logger.debug(f"Evento {event_name} publicado con éxito para log_id: {log.id}")
            
        except Exception as e:
            # Safe Error Handling: Registramos el error internamente pero NO lanzamos 
            # la excepción. La auditoría ya se guardó en PostgreSQL, que es lo vital.
            logger.error(f"Fallo al publicar evento de auditoría en Redis: {str(e)}")

    async def close(self):
        """Cierra el pool de conexiones al apagar el microservicio."""
        await self.redis.close()
        await self.pool.disconnect()