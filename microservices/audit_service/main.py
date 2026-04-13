from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine
import os

app = FastAPI(title="ISA Audit Service - Control Real")

# Conexión a la base de datos compartida
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://isa_user:isa_password@db:5432/isa_bonus_db")
engine = create_engine(DATABASE_URL)

@app.get("/")
def health():
    return {"status": "Sistema de Auditoría Operativo", "monitor": "PostgreSQL"}

@app.get("/logs-financieros")
def obtener_logs():
    try:
        # 1. Leemos la tabla directamente
        df = pd.read_sql("SELECT * FROM bonos_calculados", engine)
        
        if df.empty:
            return {"mensaje": "Sin registros. Realiza un cálculo en el puerto 8002 primero."}

        # 2. Definimos la columna exacta que vimos en tu base de datos
        columna_monto = "monto_bono" 

        # 3. Construimos el reporte financiero
        reporte = {
            "total_pagado_acumulado": float(df[columna_monto].sum()),
            "bono_promedio_otorgado": float(df[columna_monto].mean()),
            "bono_mas_alto": float(df[columna_monto].max()),
            "total_operaciones": len(df),
            "alertas_fraude": []
        }

        # Lógica de Auditoría: Detectar pagos fuera de rango (ej. > 100,000)
        sospechosos = df[df[columna_monto] > 100000]['empleado'].tolist()
        if sospechosos:
            reporte["alertas_fraude"].append(f"ALERTA: Revisar montos excedidos en: {sospechosos}")

        return {
            "resumen_ejecutivo": reporte,
            "detalle_base_datos": df.to_dict(orient="records")
        }
    except Exception as e:
        # Si algo falla, mostramos qué columnas existen realmente para depurar
        return {
            "error": "Error de sincronización con la DB",
            "detalle_tecnico": str(e)
        }