import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.infrastructure.database.database import Base
from app.infrastructure.database.models import *
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres_secure_password_2024@reports_db:5432/isa_db")
if not DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql", "postgresql+asyncpg")

async def init_models():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

asyncio.run(init_models())
