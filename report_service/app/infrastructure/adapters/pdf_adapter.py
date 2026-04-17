"""infrastructure.pdf.weasyprint_report_generator
Generador de PDF utilizando WeasyPrint.
Convierte el HTML (previamente inyectado con estilos RAG) a un documento binario.
"""
import logging
import inspect
from weasyprint import HTML

try:
    import pydyf
except ImportError:
    pydyf = None

logger = logging.getLogger("ms_reports.weasyprint")

class WeasyPrintReportGenerator:
    @staticmethod
    def _apply_pydyf_patch():
        """Aplica un parche si pydyf.PDF.__init__ no acepta los argumentos de WeasyPrint."""
        if pydyf is not None:
            try:
                sig = inspect.signature(pydyf.PDF.__init__)
                # Si solo acepta 'self', envolvemos la clase para que acepte (version, identifier)
                if len(sig.parameters) == 1:
                    original_init = pydyf.PDF.__init__
                    def patched_init(self, version=None, identifier=None):
                        original_init(self)
                        # FIX CRÍTICO: Forzar a que la versión SIEMPRE sea tipo 'bytes'
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

    @staticmethod
    def generate_pdf(html_content: str) -> bytes:
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