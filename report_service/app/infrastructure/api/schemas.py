# app/infrastructure/api/schemas.py
from pydantic import BaseModel, Field

class GenerateReportRequest(BaseModel):
    evaluacion_id: str = Field(..., description="UUID de la evaluación en la base de datos de ISA")
    profile_name: str = Field(default="General", description="Perfil de diseño a buscar en Qdrant (ej. SEP_Oficial)")
    institution_id: str = Field(default="default", description="ID de la institución para inyectar su logo dinámicamente")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "evaluacion_id": "55b85f64-3333-4444-b3fc-2c963f66afa5",
                "profile_name": "Directivos_Nivel_A",
                "institution_id": "ISA_Corp"
            }
        }
    }