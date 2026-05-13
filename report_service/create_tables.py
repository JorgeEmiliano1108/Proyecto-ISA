from sqlalchemy import create_engine
from app.infrastructure.database.database import Base
from app.infrastructure.database.models import *
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres_secure_password_2024@reports_db:5432/isa_db")
engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))
Base.metadata.create_all(bind=engine)
print("Tablas creadas exitosamente.")
