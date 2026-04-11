# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Approval Workflow Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@approval_db:5432/approval_db"
    REDIS_URL: str = "redis://approval_redis:6379/0"
    USER_SERVICE_URL: str = "http://backend_django:8000"

    # NUEVO: Bandera para usar mocks en desarrollo
    USE_MOCK_SERVICES: bool = True 

    # Permite leer desde un archivo .env si existe localmente
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()