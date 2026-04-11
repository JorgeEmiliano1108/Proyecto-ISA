# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos configuraciones y enrutadores
from app.core.config import settings
from app.infrastructure.api.routers import router as approval_router

# Importamos el motor y la base para crear las tablas
from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base

# Ciclo de vida de la aplicación (Lifespan)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Se ejecuta antes de que la API empiece a recibir peticiones
    print("Sincronizando modelos con la base de datos...")
    async with engine.begin() as conn:
        # Crea las tablas (evaluation_workflows y approval_signatures) si no existen
        await conn.run_sync(Base.metadata.create_all)
    print("Base de datos sincronizada exitosamente.")
    
    yield # La API está viva y funcionando
    
    # SHUTDOWN: Se ejecuta cuando detienes el contenedor
    print("Cerrando conexiones a la base de datos...")
    await engine.dispose()

# Inicialización de FastAPI

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de flujos de aprobación (Máquina de Estados) para ISA Corporativo.",
    version="1.0.0",
    lifespan=lifespan # Inyectamos el ciclo de vida aquí
)

# Configuración estricta de CORS (OWASP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, restringir a los dominios de ISA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(approval_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de monitoreo para orquestadores (Docker/Kubernetes)."""
    return {"status": "ok", "service": settings.PROJECT_NAME}