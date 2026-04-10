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
    
    # ---------------------------------------------------------
    # 1. Metadatos del Entorno y API
    # ---------------------------------------------------------
    PROJECT_NAME: str = "Audit & Logging Service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # ---------------------------------------------------------
    # 2. Seguridad Criptográfica (OWASP)
    # ---------------------------------------------------------
    # SecretStr evita que el valor se filtre si se hace print(settings) en los logs.
    # Esta llave se usa en security.py para el HMAC (Tamper-Evidence).
    SECRET_KEY: SecretStr 

    
    # Base de Datos (PostgreSQL async)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Construye la URI de conexión de forma segura utilizando el driver asíncrono.
        """
        # Extraemos el string real del SecretStr solo en el momento de la conexión
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


    # Mensajería / Caché (Redis)

    # Necesario para publicar los eventos asíncronos que consumirá la IA
    REDIS_SERVER: str
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_SERVER}:{self.REDIS_PORT}/0"

   
    # Configuración de Pydantic

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )


settings = Settings()