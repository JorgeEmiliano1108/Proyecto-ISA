"""app/infrastructure/adapters/vector_adapter.py

Adaptador Qdrant para la recuperación de Reglas de Diseño (RAG).
Implementa VectorDBPort y utiliza búsqueda de similitud semántica.
"""

import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue

# Importaciones de la Arquitectura Hexagonal
from app.core.config import settings
from app.application.ports.output import VectorDBPort, LLMPort

logger = logging.getLogger("ms_reports.qdrant")

class QdrantAdapter(VectorDBPort):
    def __init__(self, llm_adapter: LLMPort):
        """
        Inyección de dependencias: Qdrant no sabe qué LLM (Ollama, OpenAI, etc.) 
        se está usando. Solo exige un objeto que cumpla con el contrato LLMPort 
        para generar los embeddings.
        """
        self.llm_adapter = llm_adapter
        
        clean_url = settings.QDRANT_URL.replace("http://", "")
        host = clean_url.split(":")[0]
        port = int(clean_url.split(":")[1]) if ":" in clean_url else 6333
        
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = settings.QDRANT_COLLECTION

    # =========================================================================
    # IMPLEMENTACIÓN DEL PUERTO (VectorDBPort)
    # =========================================================================
    def get_style_rules(self, profile_name: str) -> str:
        """
        Busca fragmentos del Manual de Identidad en la base vectorial 
        usando embeddings generados al vuelo.
        """
        # Formulamos y normalizamos la consulta semántica
        query = f"Estructura para {profile_name}"
        normalized_query = query.lower().strip()

        try:
            # Usamos el contrato LLMPort para obtener el vector
            vector = self.llm_adapter.get_embedding(normalized_query)
            if not vector:
                logger.warning(f"[{profile_name}] Fallo al generar embedding. Usando fallback.")
                return "Aplica colores institucionales neutros (Azul oscuro). No incluyas logos."

            hits = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=3
            )
            
            context_chunks = [hit.payload.get("content", "") for hit in hits.points if hit.payload]
            
            if not context_chunks:
                logger.info(f"No se encontraron reglas en Qdrant para: {profile_name}")
                return "Aplica colores institucionales estándar de ISA Corporativo (#1A365D y #E2E8F0)."
                
            logger.info(f"Se recuperaron {len(context_chunks)} fragmentos de reglas para {profile_name}.")
            return "\n---\n".join(context_chunks)
            
        except Exception as e:
            logger.error(f"Error conectando a Qdrant para extraer estilos: {e}")
            return "Modo contingencia ISA. Usa diseño neutral sin recursos externos."
            
    # =========================================================================
    # MÉTODOS DE ADMINISTRACIÓN (RAG Management)
    # =========================================================================
    def upsert_rule(self, profile_name: str, text_content: str) -> str:
        """Vectoriza el texto del PDF y lo guarda en Qdrant asociado al perfil."""
        vector = self.llm_adapter.get_embedding(text_content)
        if not vector:
            raise ValueError("El motor LLM no pudo generar el embedding del documento.")
            
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE)
            )
            
        point_id = str(uuid.uuid4())
        normalized_profile = profile_name.lower().strip()
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id, 
                    vector=vector, 
                    payload={"content": text_content, "profile_name": normalized_profile}
                )
            ]
        )
        return point_id

    def delete_rule(self, profile_name: str) -> None:
        """Elimina de Qdrant todas las reglas asociadas a un perfil específico."""
        normalized_profile = profile_name.lower().strip()
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="profile_name", 
                        match=MatchValue(value=normalized_profile)
                    )
                ]
            )
        )