# app/workers/anomaly_detector.py
import asyncio
import json
import logging
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.database import AsyncSessionLocal
from app.infrastructure.database.models import AuditLogModel, AIAnomalyReportModel
from app.infrastructure.messaging.publisher import RedisEventPublisher # Para reusar el pool de conexión

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProcessValidationWorker")

OLLAMA_URL = "http://ollama:11434/api/generate" # Asumiendo que Ollama correrá en Docker


# Prompt Engineering Estricto para Modelos Pequeños (phi-3)

SYSTEM_PROMPT = """Eres un auditor de cumplimiento de Recursos Humanos estricto.
Tu trabajo es analizar registros de evaluación de desempeño y detectar anomalías lógicas, sesgos, lenguaje inapropiado o falta de congruencia.
DEBES RESPONDER ÚNICA Y EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO. No agregues texto introductorio ni explicaciones fuera del JSON.

Formato requerido:
{
  "anomaly_detected": true/false,
  "reason": "Explicación breve de por qué hay o no hay anomalía (máximo 2 oraciones)"
}
"""

async def analyze_with_phi3(action: str, details: dict) -> dict:
    """Envía el contexto al modelo local phi-3 vía Ollama."""
    
    user_prompt = f"""Analiza esta acción de RRHH:
Acción: {action}
Detalles del registro: {json.dumps(details, ensure_ascii=False)}

¿Existe alguna anomalía lógica o de cumplimiento? Responde en JSON."""

    payload = {
        "model": "phi3",
        "prompt": f"<|system|>\n{SYSTEM_PROMPT}<|end|>\n<|user|>\n{user_prompt}<|end|>\n<|assistant|>",
        "stream": False,
        "format": "json" # Ollama soporta modo JSON estricto
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # phi-3 devuelve la respuesta en result["response"]
            ai_response = json.loads(result["response"])
            return ai_response
            
        except (httpx.RequestError, json.JSONDecodeError) as e:
            logger.error(f"Error comunicándose con Ollama o parseando JSON: {e}")
            return {"anomaly_detected": False, "reason": "Error en procesamiento de IA."}


async def process_audit_event(message_data: str):
    """Orquesta la extracción de datos seguros y el análisis de IA."""
    try:
        event = json.loads(message_data)
        log_id = event["data"]["id"]
        action = event["data"]["action"]
        
        logger.info(f"Procesando evento para Log ID: {log_id}")

        async with AsyncSessionLocal() as session:
            # 1. Recuperar los datos sensibles directamente de la BD (LFPDPPP)
            query = select(AuditLogModel).where(AuditLogModel.id == log_id)
            result = await session.execute(query)
            audit_log = result.scalar_one_or_none()

            if not audit_log:
                logger.warning(f"Log ID {log_id} no encontrado en BD. Omitiendo.")
                return

            # 2. Análisis de IA (solo si la acción amerita análisis de texto, ej. rechazos o bonos)
            if action in ["STATE_TRANSITION", "ASSIGN_BONUS"] and audit_log.details:
                ai_verdict = await analyze_with_phi3(action, audit_log.details)
                
                # 3. Guardar el veredicto en la base de datos
                report = AIAnomalyReportModel(
                    audit_log_id=audit_log.id,
                    anomaly_detected=ai_verdict.get("anomaly_detected", False),
                    reason=ai_verdict.get("reason", "Sin comentarios"),
                    model_used="phi-3:mini"
                )
                session.add(report)
                await session.commit()
                
                if report.anomaly_detected:
                    logger.warning(f"ANOMALÍA DETECTADA [Log {log_id}]: {report.reason}")
                else:
                    logger.info(f"Proceso limpio [Log {log_id}]")

    except Exception as e:
        logger.error(f"Error procesando evento: {str(e)}", exc_info=True)


async def main():
    """Bucle principal de consumo de Redis."""
    logger.info("Iniciando Process Validation Worker (Phi-3)...")
    
    redis_client = RedisEventPublisher().redis
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("audit_events")
    
    logger.info("Suscrito al canal 'audit_events'. Esperando datos...")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Disparamos la tarea en background para no bloquear el consumo de la cola
                asyncio.create_task(process_audit_event(message["data"]))
    except asyncio.CancelledError:
        logger.info("Worker detenido.")
    finally:
        await pubsub.unsubscribe("audit_events")
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())