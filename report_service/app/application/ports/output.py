"""app/application/ports/output.py

Puertos de Salida (Secondary Ports).
Definen las interfaces que los adaptadores de infraestructura deben implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional  # noqa: F401
from app.domain.entities import EvaluacionISA

class ISARepositoryPort(ABC):
    """Contrato para leer la base de datos PostgreSQL de ISA Corporativo."""
    
    @abstractmethod
    def get_evaluation_full_data(self, evaluacion_id: str, requester_id: str, requester_role: str) -> Optional[EvaluacionISA]:
        """
        Debe extraer la evaluación validando estrictamente que el requester_id
        tenga autorización sobre la misma (Prevención de IDOR).
        """
        pass

    @abstractmethod
    def save_audit_log(self, job_id: str, status: str, result_url: Optional[str] = None, error: Optional[str] = None) -> None:
        """Debe guardar o actualizar el registro en escalafonia_reports_audit."""
        pass

class CloudStoragePort(ABC):
    """Contrato para interactuar con almacenamiento en nube (S3/MinIO)."""

    @abstractmethod
    def upload_pdf(self, file_bytes: bytes, file_name: str) -> None:
        """Sube el archivo PDF binario al bucket S3."""
        pass

    @abstractmethod
    def generate_presigned_url(self, file_name: str, expires_in_sec: int = 300) -> str:
        """Genera una URL temporal y firmada para la descarga segura del archivo."""
        pass

    @abstractmethod
    def delete_pdf(self, file_name: str) -> None:
        """Elimina físicamente el archivo del bucket S3 para cumplir con LFPDPPP."""
        pass

class VectorDBPort(ABC):
    """Contrato para conectarse a Qdrant (RAG)."""
    
    @abstractmethod
    def get_style_rules(self, profile_name: str) -> str:
        """Debe devolver el texto con las reglas de estilo (colores, tipografía) desde la DB Vectorial."""
        pass

class LLMPort(ABC):
    """Contrato para conectarse a Ollama (Phi-3)."""
    
    @abstractmethod
    def generate_report_layout(self, context_rules: str, sanitized_payload: Dict[str, Any]) -> dict:
        """Debe devolver un JSON estricto con la estructura del reporte."""
        pass

class PDFGeneratorPort(ABC):
    """Contrato para ensamblar HTML y generar el PDF (WeasyPrint)."""
    
    @abstractmethod
    def build_html(self, layout_schema: dict, institution_id: str) -> str:
        """Ensambla el HTML inyectando logotipos."""
        pass

    @abstractmethod
    def generate_pdf_bytes(self, html_content: str) -> bytes:
        """Convierte el HTML en un archivo PDF binario."""
        pass

class JobStorePort(ABC):
    """Contrato para Redis (Control de tareas asíncronas)."""
    
    @abstractmethod
    def update_status(self, job_id: str, status: str) -> None:
        pass
    
    @abstractmethod
    def set_result(self, job_id: str, url: str) -> None:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[dict]:
        """Recupera los datos completos de un job (estado, resultado, etc.)."""
        pass