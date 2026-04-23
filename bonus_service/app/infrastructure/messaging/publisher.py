import json
import logging
from datetime import datetime

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """
    Emite eventos al bus de mensajes Redis.
    Cumple con LFPDPPP Art. 26-27 (notificación de brechas en 72 horas).
    """

    def __init__(self):
        self._redis: aioredis.Redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def publish(self, event_type: str, payload: dict) -> None:
        sanitized_payload = self._sanitize_payload(payload)
        event = {
            "event_type": event_type,
            "service": "bonus_service",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": sanitized_payload,
        }
        channel = settings.AUDIT_REDIS_CHANNEL
        try:
            await self._redis.publish(channel, json.dumps(event))
            logger.info(f"Evento '{event_type}' publicado en canal '{channel}'")
        except Exception as exc:
            logger.error(f"Error publicando evento '{event_type}': {exc}")

    def _sanitize_payload(self, payload: dict) -> dict:
        sensitive_fields = {"salario_base_snapshot", "monto_final_bono"}
        return {k: v for k, v in payload.items() if k not in sensitive_fields}

    # ← NUEVO: Método específico para brechas de seguridad (LFPDPPP)
    async def publish_breach(self, breach_data: dict) -> None:
        breach_event = {
            "event_type": "breach.detected",
            "service": "bonus_service",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "HIGH",
            "payload": breach_data,
            "notification_deadline": "72 hours (INAI)"
        }
        try:
            await self._redis.publish(settings.AUDIT_REDIS_CHANNEL, json.dumps(breach_event))
            logger.critical(f"BRECHA DE SEGURIDAD DETECTADA: {breach_data}")
        except Exception as exc:
            logger.error(f"Error publicando brecha: {exc}")

    async def close(self) -> None:
        await self._redis.aclose()


# Instancia singleton
event_publisher = RedisEventPublisher()