"""app/core/config.py

Configuraciones centrales del microservicio de Reportes (ISA Corporativo).
Usa pydantic_settings para leer automáticamente del entorno y validar tipos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- API y Seguridad ---
    HOST: str = Field(default="0.0.0.0", alias="MS3_HOST")
    PORT: int = Field(default=8003, alias="MS3_PORT")
    
    # Llave Pública RSA (RS256) para verificar tokens emitidos por el Auth Service
    JWT_PUBLIC_KEY: str = Field(
        default="",
        description="Llave Pública RSA en formato PEM"
    )
    ALGORITHM: str = Field(default="RS256")

    # --- Base de Datos Local Compartida (PostgreSQL) ---
    DATABASE_URL: str = Field(
        default="", 
        alias="DATABASE_URL"
    )

    # --- Caché y Mensajería (Redis) ---
    REDIS_URL: str = Field(
        default="", 
        alias="MS3_REDIS_URL"
    )

    # --- Almacenamiento en Nube (S3 / MinIO) ---
    S3_ENDPOINT: str = Field(default="", alias="MS3_S3_ENDPOINT")
    S3_PUBLIC_ENDPOINT: str = Field(default="", alias="MS3_S3_PUBLIC_ENDPOINT")
    S3_ACCESS_KEY: str = Field(default="", alias="MS3_S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(default="", alias="MS3_S3_SECRET_KEY")
    S3_BUCKET: str = Field(default="reports", alias="MS3_S3_BUCKET")

    # --- Infraestructura IA Unificada (Ollama + Qdrant) ---
    OLLAMA_BASE_URL: str = Field(default="http://ollama_reports:11434")
    OLLAMA_LLM_MODEL: str = Field(default="phi3")
    OLLAMA_EMBED_MODEL: str = Field(default="nomic-embed-text")

    QDRANT_URL: str = Field(default="http://reports_qdrant:6333")
    QDRANT_COLLECTION: str = Field(default="isa_reports_styles")

    # --- Backend Django API (para fetch de datos en vez de SQL directo) ---
    BACKEND_API_URL: str = Field(
        default="http://backend_django:8000",
        description="URL base del backend Django para consultar evaluaciones via API REST"
    )
    BACKEND_INTERNAL_TOKEN: str = Field(
        default="",
        description="Token JWT o API Key para autenticarse contra el backend Django"
    )

    # Configuración del modelo
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()