# app/workers/tasks.py
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

# Importamos nuestra app de Celery
from app.workers.celery_app import celery_app

# Importamos la infraestructura de base de datos
from app.infrastructure.database.database import async_session_maker
from app.infrastructure.database.models import WorkflowModel
from app.domain.entities import EvaluationStatus

async def _check_and_notify_stalled_workflows():
    """
    Función asíncrona real que interactúa con asyncpg.
    Busca evaluaciones atoradas y simula el envío de notificaciones.
    """
    async with async_session_maker() as session:
        # Calculamos la fecha límite (Hace 3 días)
        limite_tiempo = datetime.now(timezone.utc) - timedelta(days=3)
        
        # Query optimizada: Solo traemos las que están pendientes y superaron el tiempo
        stmt = select(WorkflowModel).where(
            WorkflowModel.status == EvaluationStatus.PENDING_APPROVAL,
            WorkflowModel.updated_at <= limite_tiempo
        )
        
        result = await session.execute(stmt)
        stalled_workflows = result.scalars().all()

        if not stalled_workflows:
            print("[CRONJOB] No hay evaluaciones atoradas el día de hoy. Todo en orden.")
            return

        # Aquí integrarías el envío real de correos (ej. Amazon SES o SendGrid)
        for wf in stalled_workflows:
            # En producción, consultarías al User Service para obtener el correo del aprobador en turno
            print(f"[CRONJOB] ALERTA: La evaluación {wf.evaluation_id} lleva más de 3 días esperando firma.")
            
            # TODO: Lógica de envío de email
            # send_email(to="aprobador@isa.com.mx", template="reminder", context={"eval_id": wf.evaluation_id})

@celery_app.task(name="app.workers.tasks.send_pending_reminders", bind=True, max_retries=3)
def send_pending_reminders(self):
    """
    Envoltorio Síncrono para Celery.
    Celery llama a esta función de manera síncrona, y nosotros abrimos 
    un Event Loop de asyncio para ejecutar la consulta a PostgreSQL.
    """
    print("[CRONJOB] Iniciando barrido de base de datos para recordatorios de 3 días...")
    try:
        # Ejecutamos la corrutina asíncrona bloqueando este hilo de Celery de forma segura
        asyncio.run(_check_and_notify_stalled_workflows())
        print("[CRONJOB] Barrido finalizado exitosamente.")
    except Exception as exc:
        print(f"[CRONJOB] Error crítico durante el barrido: {str(exc)}")
        # Si la base de datos falla, Celery reintentará la tarea automáticamente hasta 3 veces
        raise self.retry(exc=exc, countdown=60) # Reintenta en 60 segundos