from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import ssl

from app.core.config import settings

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ── Motor de ESCRITURA (tabla bonos) ──────────────────────────────────────────
write_engine = create_async_engine(
    settings.write_db_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "ssl": ssl_context,
    },
)

WriteSessionLocal = async_sessionmaker(
    bind=write_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Motor de SOLO LECTURA (tabla evaluaciones) ────────────────────────────────
read_engine = create_async_engine(
    settings.read_db_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": ssl_context,
    },
)

ReadSessionLocal = async_sessionmaker(
    bind=read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


# ── Dependencias FastAPI ───────────────────────────────────────────────────────
async def get_write_session() -> AsyncSession:
    async with WriteSessionLocal() as session:
        yield session


async def get_read_session() -> AsyncSession:
    async with ReadSessionLocal() as session:
        yield session
