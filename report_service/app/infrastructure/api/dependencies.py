"""app/infrastructure/api/dependencies.py

Contenedor de Inyección de Dependencias para FastAPI.
Garantiza que los adaptadores se instancien correctamente y se 
inyecten en los casos de uso respetando la Arquitectura Hexagonal.
"""

from fastapi import Depends

# Importar Adaptadores
from app.infrastructure.database.repository import PostgresISARepository
from app.infrastructure.adapters.vector_adapter import QdrantAdapter
from app.infrastructure.adapters.llm_adapter import OllamaAdapter
from app.infrastructure.adapters.pdf_adapter import WeasyPrintReportGenerator
from app.infrastructure.messaging.job_store import JobMetadataStore

# Importar Caso de Uso
from app.application.use_cases.generate_evaluation_report import GenerateEvaluationReportUseCase

def get_job_store() -> JobMetadataStore:
    return JobMetadataStore.from_env()

def get_db_repository() -> PostgresISARepository:
    return PostgresISARepository()

def get_llm() -> OllamaAdapter:
    return OllamaAdapter()

# FIX CRÍTICO APLICADO: QdrantAdapter ahora exige un LLMPort en su constructor
def get_vector_db(llm: OllamaAdapter = Depends(get_llm)) -> QdrantAdapter:
    return QdrantAdapter(llm_adapter=llm)

def get_pdf_generator() -> WeasyPrintReportGenerator:
    return WeasyPrintReportGenerator()

def get_generate_report_use_case(
    db_repo: PostgresISARepository = Depends(get_db_repository),
    vector_db: QdrantAdapter = Depends(get_vector_db),
    llm: OllamaAdapter = Depends(get_llm),
    pdf_gen: WeasyPrintReportGenerator = Depends(get_pdf_generator),
    job_store: JobMetadataStore = Depends(get_job_store)
) -> GenerateEvaluationReportUseCase:
    """
    Ensambla el Orquestador Principal.
    FastAPI resolverá automáticamente todo el árbol de dependencias de arriba hacia abajo
    y le entregará al caso de uso sus adaptadores listos para operar.
    """
    return GenerateEvaluationReportUseCase(
        db_repo=db_repo,
        vector_db=vector_db,
        llm=llm,
        pdf_gen=pdf_gen,
        job_store=job_store
    )