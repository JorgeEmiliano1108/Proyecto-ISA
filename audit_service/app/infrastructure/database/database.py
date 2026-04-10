# app/infrastructure/database/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# 1. Creación del Engine asíncrono
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.ENVIRONMENT == "development", # Imprime queries en consola solo en dev
    future=True,
    pool_pre_ping=True, # Verifica si la conexión está viva antes de usarla (Resiliencia)
    pool_size=20,       # Preparado para alta concurrencia (NFR1)
    max_overflow=10
)

# 2. Configuración de la fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Evita errores de Lazy Loading fuera del contexto de BD
    autocommit=False,
    autoflush=False
)

# 3. Dependencia de FastAPI para inyectar la sesión
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador asíncrono que provee una sesión de BD por cada petición HTTP.
    Garantiza que la conexión se cierre correctamente (OWASP Resource Management).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()