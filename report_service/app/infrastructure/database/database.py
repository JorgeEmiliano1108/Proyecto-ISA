"""app/infrastructure/database/database.py
Configuración del motor de base de datos asíncrono.
Utiliza SQLAlchemy 2.0 y asyncpg para un alto rendimiento en la generación de reportes.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# El driver asyncpg requiere que el prefijo sea postgresql+asyncpg
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

from sqlalchemy.pool import NullPool

# Crear motor asíncrono
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass

async def get_db_session():
    """Generador de sesiones para ser usado en dependencias de FastAPI."""
    async with AsyncSessionLocal() as session:
        yield session