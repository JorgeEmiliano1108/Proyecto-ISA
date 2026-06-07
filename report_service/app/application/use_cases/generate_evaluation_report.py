"""app/application/use_cases/generate_evaluation_report.py

Orquestador central del microservicio.
Implementa el flujo: Extracción Segura (Anti-IDOR) -> Sanitización LFPDPPP -> 
RAG -> Phi3 -> PDF -> S3 Upload -> Auditoría Inmutable.
"""

import logging
import traceback

from app.application.ports.output import (
    ISARepositoryPort,
    VectorDBPort,
    LLMPort,
    PDFGeneratorPort,
    JobStorePort,
    CloudStoragePort  # <-- Contrato de S3/MinIO
)
from app.domain.sanitizer import DataSanitizer

from app.core.exceptions import ResourceNotFoundException
from app.infrastructure.monitoring.metrics import REPORT_GENERATION_ERRORS

logger = logging.getLogger("ms_reports.use_case")

class GenerateEvaluationReportUseCase:
    def __init__(
        self,
        db_repo: ISARepositoryPort,
        vector_db: VectorDBPort,
        llm: LLMPort,
        pdf_gen: PDFGeneratorPort,
        job_store: JobStorePort,
        cloud_storage: CloudStoragePort
    ):
        self.db = db_repo
        self.qdrant = vector_db
        self.llm = llm
        self.pdf_gen = pdf_gen
        self.job_store = job_store
        self.cloud_storage = cloud_storage

    def run(
        self, 
        evaluacion_id: str, 
        profile_name: str, 
        institution_id: str, 
        job_id: str,
        requester_id: str,     
        requester_role: str    
    ) -> None:
        
        # Importación local para evitar dependencias circulares con Celery
        from app.workers.tasks import delete_ephemeral_report

        try:
            self.job_store.update_status(job_id, "STARTED")
            logger.info(f"[{job_id}] Iniciando generación para evaluación: {evaluacion_id}")

            # 1. EXTRACCIÓN SEGURA (Prevención de IDOR en la BD)
            eval_data = self.db.get_evaluation_full_data(evaluacion_id, requester_id, requester_role)
            if not eval_data:
                # CORRECCIÓN: Usamos la excepción segura de nuestro core
                raise ResourceNotFoundException(
                    message=f"Evaluación no encontrada o acceso denegado para ID: {evaluacion_id}",
                    details={"evaluacion_id": evaluacion_id}
                )

            # 2. SANITIZACIÓN Y PRIVACIDAD (LFPDPPP)
            logger.info(f"[{job_id}] Enmascarando datos personales (PII)...")
            raw_dict = eval_data.model_dump()
            safe_payload = DataSanitizer.sanitize_evaluation_payload(raw_dict)

            # 3. RAG: Buscar reglas de diseño en Qdrant
            logger.info(f"[{job_id}] Buscando reglas de diseño para: {profile_name}")
            try:
                context_rules = self.qdrant.get_style_rules(f"Estructura para {profile_name}")
            except Exception as e:
                logger.warning(f"[{job_id}] Base vectorial falló o vacía. Usando default. Error: {e}")
                context_rules = ""

            if not context_rules:
                context_rules = f"""
                Eres un diseñador de reportes corporativos. DEBES obedecer este esquema:
                1. Título principal: "Evaluación de Desempeño Discrecional".
                2. Subtítulo: "{profile_name}".
                3. Analiza el desempeño del empleado basándote en las 'competencias' y la 'calificacion_global'.
                4. Genera una sección 'key_value' para datos descriptivos.
                5. Genera una sección 'chart' para las calificaciones de las competencias.
                6. NO inventes información. Usa SOLO los datos sanitizados proporcionados.
                """

            # 4. LLM: Generar Layout Estructurado con Phi-3
            logger.info(f"[{job_id}] Generando layout universal con IA Local...")
            layout_schema = self.llm.generate_report_layout(context_rules, safe_payload)

            # 5. ENSAMBLAJE HTML Y PDF (En Memoria RAM)
            logger.info(f"[{job_id}] Ensamblando HTML y renderizando PDF...")
            html_content = self.pdf_gen.build_html(layout_schema, institution_id)
            pdf_bytes = self.pdf_gen.generate_pdf_bytes(html_content)

            # 6. ALMACENAMIENTO EFÍMERO EN NUBE (S3/MinIO)
            filename = f"report_{job_id}.pdf"
            logger.info(f"[{job_id}] Subiendo PDF a almacenamiento seguro (S3)...")
            self.cloud_storage.upload_pdf(pdf_bytes, filename)
            
            # Generamos URL segura válida solo por 5 minutos
            public_url = self.cloud_storage.generate_presigned_url(filename, expires_in_sec=300)

            # 7. FINALIZACIÓN Y AUDITORÍA INMUTABLE
            self.job_store.set_result(job_id, public_url)
            self.job_store.update_status(job_id, "SUCCESS")
            
            self.db.save_audit_log(
                job_id=job_id, 
                status="AVAILABLE", 
                result_url=public_url
            )

            # 8. AUTODESTRUCCIÓN ASÍNCRONA
            logger.info(f"[{job_id}] Reporte subido. Programando destrucción física en S3 en 5 min...")
            delete_ephemeral_report.apply_async(args=[job_id, filename], countdown=300)

        except Exception as exc:
            tb = traceback.format_exc()
            logger.error(f"[{job_id}] Fallo crítico: {tb}")
            REPORT_GENERATION_ERRORS.labels(error_type="use_case").inc()
            
            self.job_store.update_status(job_id, "FAILED")
            self.job_store.set_result(job_id, "") 
            
            self.db.save_audit_log(
                job_id=job_id, 
                status="FAILED", 
                error=str(exc)
            )
            raise