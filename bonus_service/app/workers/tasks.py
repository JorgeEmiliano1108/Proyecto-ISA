import asyncio
import logging
from typing import List, Optional

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="bonus.calculate_batch", max_retries=3, default_retry_delay=60)
def calculate_bonos_batch_task(self, registros: List[dict]) -> dict:
    """
    Tarea Celery que ejecuta el cálculo masivo de bonos en segundo plano.
    Ahora recibe 'calculado_por' en cada registro para trazabilidad LFPDPPP.
    """
    try:
        result = asyncio.run(_process_batch(registros))
        return result
    except Exception as exc:
        logger.error(f"Error en calculate_bonos_batch_task: {exc}")
        raise self.retry(exc=exc)


async def _process_batch(registros: List[dict]) -> dict:
    """Lógica asíncrona real: cálculo → persistencia → eventos."""
    from app.domain.calculator import calcular_bonos_batch
    from app.infrastructure.database.database import WriteSessionLocal
    from app.infrastructure.database.repository import SQLBonusRepository
    from app.infrastructure.messaging.publisher import event_publisher

    # 1. Cálculo vectorizado (dominio puro — sin I/O)
    bonus_entities = calcular_bonos_batch(registros)

    # Obtenemos el usuario que solicitó el batch (viene del router)
    calculado_por: Optional[str] = None
    if registros and "calculado_por" in registros[0]:
        calculado_por = registros[0]["calculado_por"]

    # 2. Persistencia batch (con trazabilidad LFPDPPP)
    async with WriteSessionLocal() as session:
        repo = SQLBonusRepository(session)
        total_guardados = await repo.save_batch(
            bonuses=bonus_entities,
            calculado_por=calculado_por,          # ← NUEVO: trazabilidad
        )

    # 3. Emisión de eventos de auditoría por cada bono
    for bonus in bonus_entities:
        await event_publisher.publish("bonus.assigned", bonus.to_dict())

    logger.info(
        f"Batch completado: {total_guardados} bonos calculados y persistidos "
        f"por usuario {calculado_por or 'batch_system'}"
    )
    return {"status": "completed", "total_procesados": total_guardados}