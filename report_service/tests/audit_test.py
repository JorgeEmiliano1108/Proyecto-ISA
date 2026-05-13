import requests
import time
import jwt # PyJWT
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
BASE_URL = "http://localhost:8004/api/v1"
# Usamos la misma llave privada que generamos para mock_auth.py
try:
    with open("dev_private.pem", "r") as f:
        PRIVATE_KEY = f.read()
except FileNotFoundError:
    print("❌ Error: Necesitas el archivo dev_private.pem generado anteriormente.")
    exit(1)

def generate_token(role="RRHH"):
    payload = {
        "sub": "22222222-2222-2222-2222-222222222222",
        "role": role,
        "jti": "test-audit-unique-id",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

TOKEN = generate_token()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def run_audit():
    print("🛡️ Iniciando Auditoría de report_service...\n")

    # 1. Probar Seguridad (Acceso denegado sin token)
    print("Step 1: Validando Seguridad (401)...")
    r = requests.get(f"{BASE_URL}/status/test", headers={})
    if r.status_code in [401, 403]:
        print("✅ Correcto: Acceso bloqueado sin credenciales.")
    else:
        print(f"❌ Error en Seguridad, se esperaba 401, se obtuvo: {r.status_code}")

    # 2. Subir Reglas de Negocio (RAG)
    print("\nStep 2: Inyectando Reglas de RAG (PDF)...")
    with open("reglas_directivos.pdf", "rb") as f:
        files = {"file": ("reglas_directivos.pdf", f, "application/pdf")}
        data = {"profile_name": "AgroGuard_Standard"} # Usando un perfil agrícola para tu proyecto
        r = requests.post(f"{BASE_URL}/rules/upload", headers=HEADERS, files=files, data=data)
        
    if r.status_code == 201:
        print("✅ Correcto: Reglas vectorizadas en Qdrant.")
    else:
        print(f"❌ Error en RAG: {r.status_code} - {r.text}")

    # 3. Disparar Generación de Reporte (Con PII para probar Sanitizer)
    print("\nStep 3: Disparando generación de reporte (Con PII para sanitizar)...")
    eval_payload = {
        "evaluacion_id": "c6a84c56-6a56-4b56-8a56-06a56a56a56a", # UUID ficticio
        "profile_name": "AgroGuard_Standard",
        "institution_id": "ISA_CDMX_01",
        "evaluado_id": "user_99",
        # Metemos un RFC real para ver si el DataSanitizer lo mata
        "comentarios_extra": "El empleado con RFC: VECM930101XYZ ha mostrado gran desempeño."
    }
    
    r = requests.post(f"{BASE_URL}/generate", headers=HEADERS, json=eval_payload)
    if r.status_code == 202:
        job_id = r.json().get("job_id")
        print(f"✅ Correcto: Tarea aceptada. Job ID: {job_id}")
    else:
        print(f"❌ Error al generar: {r.status_code} - {r.text}")
        return

    # 4. Polling de Status (Celery + Redis)
    print("\nStep 4: Monitoreando progreso en Celery...")
    for _ in range(15):
        res = requests.get(f"{BASE_URL}/status/{job_id}", headers=HEADERS)
        status = res.json().get("status")
        print(f"   > Estado actual: {status}")
        
        if status == "SUCCESS":
            pdf_url = res.json().get("result_url")
            print(f"\n🎉 ¡REPORTE LISTO!: {pdf_url}")
            break
        elif status == "FAILED":
            print(f"❌ La tarea falló: {res.json().get('error')}")
            break
        time.sleep(5)

    # 5. Verificación de Auditoría en DB
    print("\nStep 5: Verificando persistencia inmutable en Postgres...")
    # Aquí podrías usar una conexión directa a SQL si quieres ser más estricto
    print("🔍 Audit Log: Consulta manual en DB: SELECT * FROM isa_reports_audit WHERE job_id='...'")

if __name__ == "__main__":
    run_audit()
