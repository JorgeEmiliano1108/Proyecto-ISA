from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ── Base de Datos ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres.pkihspbkksoggvvwcbam:admin_database2026@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
    
    DB_USER: str = "postgres.pkihspbkksoggvvwcbam"
    DB_NAME: str = "postgres"
    DB_HOST: str = "aws-1-us-west-2.pooler.supabase.com"
    DB_PORT: int = 6543
    DB_PASSWORD: str = "admin_database2026"

    EVAL_DB_USER: str = "postgres.pkihspbkksoggvvwcbam"
    EVAL_DB_NAME: str = "postgres"
    EVAL_DB_HOST: str = "aws-1-us-west-2.pooler.supabase.com"
    EVAL_DB_PORT: int = 6543
    EVAL_DB_PASSWORD: str = "admin_database2026"

    DB_MODE: str = "development"
    DEBUG_MODE: bool = True

    # ── Redis / Celery ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://bonus_redis:6379/0"
    CELERY_BROKER_URL: str = "redis://bonus_redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://bonus_redis:6379/1"

    # ── Seguridad ─────────────────────────────────────────────────────────
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    SECRET_KEY: str = "django-insecure-57-26-a-g==ub08@6koz(u5g6l)bbs7%kb%&fphy%7k8$4w9i9"
    JWT_PUBLIC_KEY: str = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr5lh1kOErXFHzGuSqqQL\ngqQJyR/OwqQQ+dwtbCM6hpRk1LlfU2MKCSwC9BhhYpQNoUapoungTeiuI6s+4wq9\n/ke8tcbSjEaG4O0JhDBaJjXp1JBarWwh7a1dtRkdhXdMQwimIYGD2EH6RXQ7MCA8\n4mHzMm5yGJ5PiclocJC7wxlG6XVpPfzIIlQR+1uDE1XaBYoM6LPxt9b9Z20NTCr6\nKdR/+LpUi2FiGk//vOOmaQcms5tulsCUPC1d3fhV87B3yyvepZ5yNzq9SZlNb704\nuceRSoexCsj4hvjtH+LwvanqselL7uM/lk2OZRsMIBaw1PmWTGjLmdM+3ELTS4n/\npwIDAQAB\n-----END PUBLIC KEY-----"
    INTERNAL_API_KEY: str = "isa_internal_key_2026"
    
    @field_validator("JWT_PUBLIC_KEY", mode="before")
    @classmethod
    def _fix_newlines(cls, v: str) -> str:
        """Convert literal \n to actual newlines in PEM keys, and strip quotes."""
        import logging
        logger = logging.getLogger(__name__)
        if isinstance(v, str):
            logger.info(f"JWT_PUBLIC_KEY validator called, length: {len(v)}")
            # Strip surrounding quotes if present (from .env file or env var)
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
                logger.info("Stripped surrounding quotes")
            # Convert literal \n to actual newlines (Docker Compose/env vars pass literal \n)
            if "\\n" in v:
                result = v.replace("\\n", "\n")
                logger.info(f"Fixed newlines, new length: {len(result)}")
                return result
        return v
    ENCRYPTION_KEY: str = "reemplazar-con-llave-fernet-32-bytes"

    AUDIT_REDIS_CHANNEL: str = "audit.events"

    @property
    def PUBLIC_KEY(self) -> Optional[str]:
        return self.JWT_PUBLIC_KEY

    @property
    def write_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def read_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.EVAL_DB_USER}:{self.EVAL_DB_PASSWORD}@{self.EVAL_DB_HOST}:{self.EVAL_DB_PORT}/{self.EVAL_DB_NAME}"


settings = Settings()