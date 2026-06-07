# app/core/config.py
from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    """
    Configuración centralizada del microservicio.
    Se alimenta de las variables de entorno o del archivo .env.
    Pydantic v2 en strict mode validará los tipos en tiempo de arranque.
    """

    # Metadatos del Entorno y API
   
    PROJECT_NAME: str = "Audit & Logging Service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    

    # Seguridad Criptográfica (OWASP)
    
    SECRET_KEY: SecretStr
    JWT_PUBLIC_KEY: str = ""

   
    # Base de Datos (PostgreSQL async)
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construye la URI de conexión de forma segura utilizando el driver asíncrono."""
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

   
    # Mensajería / Caché (Redis)

    REDIS_SERVER: str
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_SERVER}:{self.REDIS_PORT}/0"

   
    # Inteligencia Artificial (Ollama)
 
    OLLAMA_SERVER: str = "ollama"
    OLLAMA_PORT: int = 11434

    @computed_field
    @property
    def OLLAMA_URL(self) -> str:
        return f"http://{self.OLLAMA_SERVER}:{self.OLLAMA_PORT}/api/generate"

    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()