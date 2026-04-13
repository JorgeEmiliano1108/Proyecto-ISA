from celery import Celery
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("tasks", broker=CELERY_BROKER_URL)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class RegistroBono(Base):
    __tablename__ = "bonos_calculados"
    id = Column(Integer, primary_key=True)
    empleado = Column(String)
    monto_bono = Column(Float)

@celery_app.task
def guardar_bono_async(empleado, monto):
    db = SessionLocal()
    nuevo = RegistroBono(empleado=empleado, monto_bono=monto)
    db.add(nuevo)
    db.commit()
    db.close()
    return f"Bono de {empleado} guardado."
@celery_app.task
def guardar_bono_async(empleado, monto):
    # ... tu código de guardado en DB que ya funciona ...
    
    # Esto es lo único nuevo: publicamos un evento "invisible"
    celery_app.send_task("audit_tasks.registrar_auditoria", args=[empleado, monto])