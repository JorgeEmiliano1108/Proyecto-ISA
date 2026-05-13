import requests
import jwt
import time
from datetime import datetime, timedelta

# --- Configuración ---
BASE_URL = "http://localhost:8003/api/v1"
EVALUATION_ID = "c6a84c56-6a56-4b56-8a56-06a56a56a56a"
ROLE = "RRHH"
PRIVATE_KEY_PATH = "dev_private.pem"
MAGIC_BYTES_PDF = b"%PDF-"

def load_private_key():
    with open(PRIVATE_KEY_PATH, "r") as f:
        return f.read()

def generate_token():
    private_key = load_private_key()
    payload = {
        "sub": EVALUATION_ID,
        "role": ROLE,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def test_pipeline():
    print("🚀 Iniciando Test E2E de Generación de Reportes PDF...")

    # 1. Generación de Credenciales
    print("\n[Paso 1] Generando JWT...")
    try:
        token = generate_token()
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ JWT generado correctamente.")
    except Exception as e:
        print(f"❌ Error al generar JWT: {e}")
        return

    # 2. Disparo de la Generación
    print(f"\n[Paso 2] Disparando generación para {EVALUATION_ID}...")
    generate_url = f"{BASE_URL}/generate"
    payload = {
        "evaluacion_id": EVALUATION_ID,
        "profile_name": "Directivos_Nivel_A",
        "institution_id": "ISA_CDMX_01"
    }
    
    response = requests.post(generate_url, json=payload, headers=headers)
    
    if response.status_code in [401, 403]:
        print("❌ Fallo de Autenticación/Permisos.")
        return
    elif response.status_code == 422:
        print(f"❌ Error de validación Pydantic: {response.json()}")
        return
    elif response.status_code != 202:
        print(f"❌ Error inesperado al generar: HTTP {response.status_code} - {response.text}")
        return
        
    data = response.json()
    job_id = data.get("job_id")
    print(f"✅ Tarea aceptada. Job ID: {job_id}")

    # 3. Polling Asíncrono
    print("\n[Paso 3] Iniciando polling asíncrono...")
    status_url = f"{BASE_URL}/status/{job_id}"
    max_retries = 36  # 36 * 5s = 3 minutos
    
    result_url = None
    for _ in range(max_retries):
        status_res = requests.get(status_url, headers=headers)
        if status_res.status_code != 200:
            print(f"❌ Error consultando estado: HTTP {status_res.status_code} - {status_res.text}")
            return
            
        status_data = status_res.json()
        current_status = status_data.get("status")
        print(f"   > Estado actual: {current_status}")
        
        if current_status == "SUCCESS":
            result_url = status_data.get("download_url")
            if result_url:
                result_url = result_url.replace("http://minio:9000", "http://localhost:9003")
            print("✅ Procesamiento completado con éxito.")
            break
        elif current_status == "FAILED":
            # Para extraer el mensaje de error exacto, el API original no devuelve el error completo
            # en /status, pero indicamos FAILED de acuerdo a la especificación.
            print(f"❌ La tarea falló. {status_data}")
            return
            
        time.sleep(5)
        
    if not result_url:
        print("❌ Timeout superado (3 minutos) o la URL de descarga está vacía.")
        return

    # 4. Validación y Descarga
    print(f"\n[Paso 4] Descargando artefacto desde: {result_url}")
    try:
        pdf_res = requests.get(result_url)
        if pdf_res.status_code != 200:
            print(f"❌ Error al descargar de MinIO: HTTP {pdf_res.status_code} - {pdf_res.text}")
            return
            
        pdf_content = pdf_res.content
        if not pdf_content.startswith(MAGIC_BYTES_PDF):
            print("❌ El archivo descargado NO es un PDF válido (Faltan Magic Bytes).")
            return
            
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_content)
            
        print("✅ Archivo validado y guardado como 'test_output.pdf'. Flujo 100% exitoso.")
        
    except Exception as e:
        print(f"❌ Excepción durante la descarga: {e}")

if __name__ == "__main__":
    test_pipeline()
