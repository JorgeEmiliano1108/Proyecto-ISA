from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import create_engine
import os

# Importamos la tarea de Celery para persistencia asíncrona
from tasks import guardar_bono_async 

app = FastAPI(
    title="ISA Bonus Service - Analítica Avanzada",
    description="Motor de cálculo de bonos con procesamiento vectorial y persistencia desacoplada"
)

# --- Configuración de Base de Datos ---
# Se usa para el endpoint de historial (Lectura directa)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://isa_user:isa_password@db:5432/isa_bonus_db")
engine = create_engine(DATABASE_URL)

# --- Modelos de Datos (Pydantic v2) ---
class KPISchema(BaseModel):
    nombre: str = Field(..., example="Disponibilidad")
    logro: float = Field(..., ge=0, description="Valor alcanzado")
    meta: float = Field(..., gt=0, description="Valor objetivo")
    peso: float = Field(..., gt=0, le=1, description="Peso del KPI (0.0 a 1.0)")

class CalculoRequest(BaseModel):
    empleado: str = Field(..., example="INGENIERO ISA")
    salario_base: float = Field(..., gt=0)
    kpis: List[KPISchema]

# --- Endpoints ---

@app.get("/")
def health_check():
    """Verifica que el servicio de bonos esté en línea (Puerto 8002)"""
    return {"status": "Online", "service": "ISA Bonus Engine", "puerto": 8002}

@app.get("/historial-bonos")
def obtener_historial():
    """
    Recupera los datos guardados por el Worker. 
    Usa Pandas para una lectura eficiente de la base de datos.
    """
    try:
        # Ordenamos por el registro más reciente
        query = "SELECT * FROM bonos_calculados ORDER BY id DESC"
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"mensaje": "Historial no disponible", "error": str(e)}

@app.post("/calcular-pro")
async def calcular_bono_pro(data: CalculoRequest):
    """
    1. Procesa datos con lógica analítica (Pandas/NumPy).
    2. Delega el guardado a Celery (Independencia total).
    """
    try:
        # 1. Transformación analítica
        df = pd.DataFrame([k.model_dump() for k in data.kpis])
        
        # 2. Cálculo Vectorizado con NumPy
        # Limitamos cumplimiento al 100% (1.0) para evitar bonos infinitos
        df['cumplimiento'] = np.minimum(df['logro'] / df['meta'], 1.0)
        
        # Cálculo del puntaje global ponderado
        puntaje_total = (df['cumplimiento'] * df['peso']).sum()
        
        # Resultado monetario final
        monto_final = round(float(data.salario_base * puntaje_total), 2)

        # 3. Disparo Asíncrono (Fire and Forget)
        # Se envía a Redis para que el worker lo guarde sin bloquear al API
        guardar_bono_async.delay(data.empleado, monto_final)

        return {
            "status": "Procesado",
            "resultado": {
                "empleado": data.empleado,
                "monto_calculado": monto_final,
                "puntaje_global": f"{round(puntaje_total * 100, 2)}%"
            },
            "info": "Guardado en progreso vía Celery. Consultar en /historial-bonos"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el motor de cálculo: {str(e)}")