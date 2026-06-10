import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def publish_event(event_type: str, evaluacion_id: str, estado_anterior: str, estado_nuevo: str, actor_id: str, comentario: str = ""):
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL)
        message = json.dumps({
            "event_type": event_type,
            "evaluacion_id": str(evaluacion_id),
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "actor_id": str(actor_id),
            "comentario": comentario,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        })
        r.publish("audit_events", message)
        logger.info(f"Evento publicado: {event_type} - {evaluacion_id}")
    except Exception as e:
        logger.warning(f"No se pudo publicar evento Redis: {e}")
