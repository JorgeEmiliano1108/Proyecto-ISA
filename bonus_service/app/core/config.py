from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


def _read_secret(secret_name: str, required: bool = True) -> str:
    """
    Lee secreto desde Docker Secret (/run/secrets/) con prioridad absoluta.
    
    OWASP A02: Cryptographic Failures - Rotation de llaves
    
    Para rotar una llave:
    1. Subir nuevo archivo a /secrets/<secret_name>.new
    2. Reiniciar contenedor
    3. El sistema automáticamente usa la nueva llave
    4. Opcional: eliminar archivo antiguo
    """
    secrets_dir = Path("/run/secrets")

    # 1. Buscar versión nueva (para rotación hot)
    new_secret_path = secrets_dir / f"{secret_name}.new"
    if new_secret_path.is_file():
        logger.info(f"Usando nueva versión de secreto: {secret_name}.new")
        return new_secret_path.read_text().strip()

    # 2. Buscar versión principal
    secret_path = secrets_dir / secret_name
    if secret_path.is_file():
        return secret_path.read_text().strip()

    # 3. Error si es requerido (producción)
    if required:
        logger.error(f"Secreto requerido no encontrado: {secret_name}")
        raise ValueError(f"Secreto no encontrado en /run/secrets/{secret_name}")

    return ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ── Base de Datos ─────────────────────────────────────────────────────
    DB_USER: str = "postgres"
    DB_NAME: str = "postgres"
    DB_HOST: str = "aws-1-us-west-2.pooler.supabase.com"
    DB_PORT: int = 5432
    DB_PASSWORD: str = "admin_database2026"

    EVAL_DB_USER: str = "postgres"
    EVAL_DB_NAME: str = "postgres"
    EVAL_DB_HOST: str = "aws-1-us-west-2.pooler.supabase.com"
    EVAL_DB_PORT: int = 5432
    EVAL_DB_PASSWORD: str = "admin_database2026"

    DB_MODE: str = "production"
    DEBUG_MODE: bool = True

    # ── Redis / Celery ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://bonus_redis:6379/0"
    CELERY_BROKER_URL: str = "redis://bonus_redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://bonus_redis:6379/1"

    # ── Seguridad ─────────────────────────────────────────────────────────
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    SECRET_KEY: str = "7fK9pL2mX8qR4tV6wY3zN5bH8jF0cD2eA1sQ9wE3rT5yU7iO9pL2mX4vB6nZ8qR0t"
    ENCRYPTION_KEY: str = "jbFXfePbPiqSgj079V0S4AkoOBhkSY5qwGJeuU2MBXY="

    AUDIT_REDIS_CHANNEL: str = "audit.events"

    @property
    def PUBLIC_KEY(self) -> Optional[str]:
        return None

    @property
    def write_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def read_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.EVAL_DB_USER}:{self.EVAL_DB_PASSWORD}@{self.EVAL_DB_HOST}:{self.EVAL_DB_PORT}/{self.EVAL_DB_NAME}"


settings = Settings()