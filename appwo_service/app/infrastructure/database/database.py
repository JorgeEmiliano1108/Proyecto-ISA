# app/infrastructure/database/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Motor asíncrono para máximo rendimiento
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Fábrica de sesiones
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    """Generador de sesiones para inyección de dependencias."""
    async with async_session_maker() as session:
        yield session