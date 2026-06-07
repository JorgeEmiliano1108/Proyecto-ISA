"""infrastructure.pdf.weasyprint_report_generator
Generador de PDF utilizando WeasyPrint.
Convierte el HTML (previamente inyectado con estilos RAG) a un documento binario.
"""
import logging
import inspect
import os
from datetime import datetime
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

try:
    import pydyf
except ImportError:
    pydyf = None

logger = logging.getLogger("ms_reports.weasyprint")

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

class WeasyPrintReportGenerator:
    def __init__(self):
        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    @staticmethod
    def _apply_pydyf_patch():
        """Aplica un parche si pydyf.PDF.__init__ no acepta los argumentos de WeasyPrint."""
        if pydyf is not None:
            try:
                sig = inspect.signature(pydyf.PDF.__init__)
                if len(sig.parameters) == 1:
                    original_init = pydyf.PDF.__init__
                    def patched_init(self, version=None, identifier=None):
                        original_init(self)
                        if version is None:
                            self.version = b'1.7'
                        elif isinstance(version, str):
                            self.version = version.encode('ascii')
                        else:
                            self.version = version
                        self.identifier = identifier
                    pydyf.PDF.__init__ = patched_init
                    logger.info("Parche de compatibilidad pydyf (Modo Bytes) aplicado exitosamente.")
            except Exception as e:
                logger.warning(f"No se pudo aplicar el parche de pydyf: {e}")

    def build_html(self, layout_schema: dict, institution_id: str) -> str:
        """Ensambla el HTML usando Jinja2 con la plantilla corporativa."""
        template = self.jinja_env.get_template("report_template.html")
        evaluado = layout_schema.get("evaluado", {})
        evaluador = layout_schema.get("evaluador", {})
        if isinstance(evaluado, dict):
            evaluado_nombre = evaluado.get("nombre_completo") or evaluado.get("nombre") or evaluado.get("username", "")
            evaluado_puesto = evaluado.get("puesto", "")
            evaluado_depto = evaluado.get("departamento", "")
        else:
            evaluado_nombre = str(evaluado)
            evaluado_puesto = ""
            evaluado_depto = ""
        if isinstance(evaluador, dict):
            evaluador_nombre = evaluador.get("nombre_completo") or evaluador.get("nombre") or evaluador.get("username", "")
        else:
            evaluador_nombre = str(evaluador)

        competencias = layout_schema.get("competencias", [])

        return template.render(
            profile_name=layout_schema.get("profile_name", layout_schema.get("header", "")),
            institution_id=institution_id,
            evaluado={"nombre": evaluado_nombre, "puesto": evaluado_puesto, "departamento": evaluado_depto},
            evaluador={"nombre": evaluador_nombre},
            periodo=layout_schema.get("periodo", ""),
            fecha_evaluacion=layout_schema.get("fecha_evaluacion", ""),
            logros_previos=layout_schema.get("logros_previos", ""),
            competencias=competencias,
            calificacion_global=layout_schema.get("calificacion_global"),
            comentarios_evaluador=layout_schema.get("comentarios_evaluador", ""),
            comentarios_evaluado=layout_schema.get("comentarios_evaluado", ""),
            bono_asignado=layout_schema.get("bono_asignado"),
            generation_date=datetime.now().strftime("%d/%m/%Y %H:%M")
        )

    @staticmethod
    def generate_pdf_bytes(html_content: str) -> bytes:
        """Renderiza HTML a PDF de manera síncrona."""
        # Aplicamos el parche justo antes de renderizar
        WeasyPrintReportGenerator._apply_pydyf_patch()
        try:
            # HTML(string) procesa el Jinja2 ya renderizado con las variables CSS
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error crítico renderizando PDF con WeasyPrint: {str(e)}")
            raise