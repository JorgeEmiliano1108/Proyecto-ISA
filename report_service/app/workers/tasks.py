"""app/workers/tasks.py

Definición de las tareas asíncronas ejecutadas por los Celery Workers.
Conecta el ecosistema de IA y bases de datos aislando la carga computacional
del hilo principal de la API HTTP.
"""
import traceback
import gc
import logging
from celery import Task

# --- Importaciones de Trazabilidad (OpenTelemetry - HI-04) ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.celery import CeleryInstrumentor

# Importaciones de la Arquitectura Hexagonal
from app.workers.celery_app import celery_app
from app.infrastructure.messaging.job_store import JobMetadataStore
from app.infrastructure.adapters.http_repository import HttpISARepository
from app.infrastructure.adapters.llm_adapter import OllamaAdapter
from app.infrastructure.adapters.vector_adapter import QdrantAdapter
from app.infrastructure.adapters.pdf_adapter import WeasyPrintReportGenerator
from app.infrastructure.adapters.s3_adapter import S3Adapter 
from app.application.use_cases.generate_evaluation_report import GenerateEvaluationReportUseCase
from app.infrastructure.monitoring.metrics import REPORT_GENERATION_ERRORS

logger = logging.getLogger("ms_reports.worker")

# ============================================================================
# CONFIGURACIÓN DE OPENTELEMETRY (Lado Consumidor/Worker)
# ============================================================================
trace.set_tracer_provider(TracerProvider())
# Al instrumentar aquí, Celery extrae automáticamente el Trace ID que mandó FastAPI
CeleryInstrumentor().instrument()

class ReportTaskBase(Task):
    """Base Task que actualiza los metadatos del job en caso de fallo crítico de Celery."""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        REPORT_GENERATION_ERRORS.labels(error_type="celery_worker").inc()
        try:
            job_id = kwargs.get("job_id")
            if not job_id and args and len(args) >= 4:
                job_id = args[3]
                
            if job_id:
                job_store = JobMetadataStore.from_env()
                job_store.update_status(job_id, "FAILED")
                
                tb = traceback.format_exc()
                sanitized_error = (tb or str(exc))[-3000:]
                job_store.set_error(job_id, sanitized_error)
                
                db = HttpISARepository()
                db.save_audit_log(job_id=job_id, status="FAILED", error=sanitized_error)
        except Exception:
            pass
        return super().on_failure(exc, task_id, args, kwargs, einfo)

# =========================================================================
# TAREA PRINCIPAL: GENERAR REPORTE (FLUJO LFPDPPP + RAG + IA + S3)
# =========================================================================
@celery_app.task(
    name="app.workers.tasks.generate_report_task",
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
    retry_jitter=True,
    base=ReportTaskBase,
)
def generate_report_task(
    self, 
    evaluacion_id: str, 
    profile_name: str, 
    institution_id: str, 
    job_id: str,
    requester_id: str,
    requester_role: str
):
    """Orquesta la generación del PDF inyectando las dependencias manualmente en el worker."""
    
    # Extraemos el Trace ID actual para propósitos de logging correlacionado
    current_span = trace.get_current_span()
    trace_id = format(current_span.get_span_context().trace_id, '032x') if current_span.is_recording() else "NO_TRACE"
    
    logger.info(f"[Trace: {trace_id}] [Job: {job_id}] Iniciando tarea en background para evaluación: {evaluacion_id}")
    
    job_store = JobMetadataStore.from_env()
    
    try:
        db_repo = HttpISARepository()
        llm = OllamaAdapter()
        vector_db = QdrantAdapter(llm_adapter=llm) 
        pdf_gen = WeasyPrintReportGenerator()
        cloud_storage = S3Adapter()
        
        usecase = GenerateEvaluationReportUseCase(
            db_repo=db_repo,
            vector_db=vector_db,
            llm=llm,
            pdf_gen=pdf_gen,
            job_store=job_store,
            cloud_storage=cloud_storage
        )
        
        usecase.run(
            evaluacion_id=evaluacion_id, 
            profile_name=profile_name, 
            institution_id=institution_id, 
            job_id=job_id,
            requester_id=requester_id,
            requester_role=requester_role
        )
        
        logger.info(f"[Trace: {trace_id}] [Job: {job_id}] Tarea de reporte completada con éxito.")
        
    except Exception as exc:
        tb = traceback.format_exc()
        sanitized_error = tb[-3000:]
        logger.error(f"[Trace: {trace_id}] [Job: {job_id}] Fallo en la tarea: {str(exc)}")
        
        try:
            job_store.set_error(job_id, sanitized_error)
        except Exception:
            pass
        finally:
            gc.collect()
        raise

# =========================================================================
# TAREA DE LIMPIEZA: PROTOCOLO EFÍMERO (S3)
# =========================================================================
@celery_app.task(
    name="app.workers.tasks.delete_ephemeral_report",
    ignore_result=True 
)
def delete_ephemeral_report(job_id: str, file_name: str):
    current_span = trace.get_current_span()
    trace_id = format(current_span.get_span_context().trace_id, '032x') if current_span.is_recording() else "NO_TRACE"
    
    logger.info(f"[Trace: {trace_id}] [Job: {job_id}] Iniciando protocolo de autodestrucción del reporte en S3...")
    
    try:
        cloud_storage = S3Adapter()
        cloud_storage.delete_pdf(file_name)
        logger.info(f"[Trace: {trace_id}] [Job: {job_id}] Archivo {file_name} eliminado exitosamente de S3.")
    except Exception as e:
        logger.error(f"[Trace: {trace_id}] [Job: {job_id}] Error al intentar eliminar el archivo de S3: {str(e)}")
        
    try:
        db = HttpISARepository()
        db.save_audit_log(job_id=job_id, status="DELETED")
        logger.info(f"[Trace: {trace_id}] [Job: {job_id}] Historial en PostgreSQL actualizado a DELETED.")
    except Exception as e:
        logger.error(f"[Trace: {trace_id}] [Job: {job_id}] Error al actualizar el estado en PostgreSQL: {str(e)}")