"""app/infrastructure/adapters/llm_adapter.py

Adaptador de IA Local (Ollama) con validación estricta (Pydantic).
Implementa LLMPort para garantizar que el LLM entregue un esquema determinista
al motor de renderizado PDF.
"""
import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

# Importaciones de la Arquitectura Hexagonal
from app.core.config import settings
from app.application.ports.output import LLMPort

logger = logging.getLogger("ms_reports.ollama")

# ==============================================================================
# CONTRATOS DE DISEÑO (ANTI-ALUCINACIÓN)
# ==============================================================================
class StyleSchema(BaseModel):
    primary_color: str = Field(default="#1A365D") # Azul corporativo oscuro por defecto
    secondary_color: str = Field(default="#E2E8F0")
    watermark_url: Optional[str] = Field(default=None)

class HeaderSchema(BaseModel):
    title: str = Field(default="Reporte de Evaluación")
    subtitle: str = Field(default="ISA Corporativo")
    logo_url: Optional[str] = Field(default=None)

class SectionSchema(BaseModel):
    type: str = Field(..., description="Tipos soportados: 'key_value', 'text', 'chart'")
    title: str = Field(default="")
    content: Optional[str] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)

class ReportLayoutSchema(BaseModel):
    style: StyleSchema = Field(default_factory=StyleSchema)
    header: HeaderSchema = Field(default_factory=HeaderSchema)
    sections: List[SectionSchema] = Field(default_factory=list)
    footer_text: str = Field(default="Documento generado automáticamente por el Sistema ISA.")


# ==============================================================================
# IMPLEMENTACIÓN DEL ADAPTADOR
# ==============================================================================
class OllamaAdapter(LLMPort):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.llm_model = settings.OLLAMA_LLM_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.timeout = 120.0

    def get_embedding(self, text: str) -> list:
        """Genera embeddings para ser consumidos por Qdrant (Base Vectorial)."""
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {"model": self.embed_model, "prompt": text}
            resp = httpx.post(url, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
        except Exception as e:
            logger.error(f"Error al generar embedding en Ollama: {e}")
        return []

    def _sanitize_json(self, raw_text: str) -> str:
        """
        Limpia la respuesta del LLM para extraer únicamente el objeto JSON.
        Mejorado para resistir inyecciones de Markdown típicas en modelos pequeños (Phi-3).
        """
        text = raw_text.replace("```json", "").replace("```", "").strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text

    def generate_report_layout(self, context_rules: str, sanitized_payload: Dict[str, Any]) -> dict:
        """
        Implementación del contrato LLMPort. Recibe datos limpios (LFPDPPP) 
        y los inyecta en el Prompt para estructurar el reporte de ISA Corporativo.
        """
        prompt = f"""
        ACTÚA COMO UN PARSER DE JSON ESTRICTO. 
        Tu única función es tomar los datos de entrada y las reglas, y combinarlos en UN SOLO OBJETO JSON.
        
        REGLAS DE DISEÑO:
        {context_rules}
        
        DATOS DE ENTRADA (EVALUACIÓN ISA CORPORATIVO):
        {json.dumps(sanitized_payload, ensure_ascii=False)}
        
        INSTRUCCIONES CRÍTICAS:
        1. Debes generar un JSON con esta estructura exacta. NO cambies los nombres de las llaves principales ('style', 'header', 'sections', 'footer_text').
        2. Dentro de 'sections', cada objeto DEBE tener una llave 'type' que solo puede ser "key_value", "text" o "chart".
        3. Analiza los DATOS DE ENTRADA. Agrupa los datos del empleado (ej. estado, calificación global) en una sección "key_value".
        4. Si encuentras calificaciones por "competencias", colócalas OBLIGATORIAMENTE en una sección "chart".
        5. Devuelve SÓLO el código JSON. Nada de saludos, ni markdown, ni explicaciones.

        EJEMPLO DE SALIDA ESPERADA:
        {{
            "style": {{
                "primary_color": "#1A365D",
                "secondary_color": "#E2E8F0",
                "watermark_url": ""
            }},
            "header": {{
                "title": "Evaluación Discrecional de Desempeño",
                "subtitle": "ISA Corporativo",
                "logo_url": ""
            }},
            "sections": [
                {{
                    "type": "key_value",
                    "title": "Resumen de la Evaluación",
                    "data": {{"Evaluado": "J*** P****", "Rol": "Gerente", "Estado": "Aprobado", "Bono Final": 15000}}
                }},
                {{
                    "type": "chart",
                    "title": "Métricas de Competencias",
                    "data": {{"Liderazgo": 5, "Innovación": 4, "Trabajo en Equipo": 4}}
                }},
                {{
                    "type": "text",
                    "title": "Comentarios del Evaluador",
                    "content": "Excelente desempeño durante el periodo."
                }}
            ],
            "footer_text": "Documento auditable generado por el Sistema ISA."
        }}
        """
        
        try:
            url = f"{self.base_url}/api/generate"
            req_payload = {
                "model": self.llm_model, 
                "prompt": prompt, 
                "stream": False, 
            }
            resp = httpx.post(url, json=req_payload, timeout=self.timeout)
            
            if resp.status_code == 200:
                raw_output = resp.json().get("response", "{}")
                
                logger.info("=== RESPUESTA CRUDA DEL LLM (PHI-3) ===")
                logger.info(raw_output)
                logger.info("=======================================")
                
                clean_json = self._sanitize_json(raw_output)
                data = json.loads(clean_json)
                
                # Validación estricta con Pydantic
                validated_model = ReportLayoutSchema(**data)
                return validated_model.model_dump()
                
        except ValidationError as ve:
            logger.error(f"Pydantic rechazó el JSON de Phi-3. Errores de esquema: {ve}")
        except json.JSONDecodeError as je:
            logger.error(f"El LLM no devolvió un JSON válido. Error de sintaxis: {je}")
        except Exception as e:
            logger.error(f"Fallo general en generación de layout: {e}")
            
        # MODO CONTINGENCIA: Si la IA falla o alucina, regresamos un reporte genérico seguro
        return ReportLayoutSchema(
            header=HeaderSchema(title="Reporte ISA Corporativo", subtitle="Modo Contingencia"),
            sections=[SectionSchema(type="text", title="Error de Procesamiento", content="El motor de IA no pudo estructurar el diseño de este reporte.")],
            footer_text="Sistema ISA - Error"
        ).model_dump()