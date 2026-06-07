"""app/infrastructure/api/routers.py
Endpoints para la generación asíncrona de reportes y gestión de activos.
Protegidos mediante validación estricta de JWT, Rate Limiting y File Security.
"""
import os
import io
import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from pypdf import PdfReader 

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.infrastructure.api.schemas import GenerateReportRequest
from app.infrastructure.api.dependencies import get_job_store, get_vector_db, get_status_use_case
from app.application.use_cases.get_report_status import GetReportStatusUseCase
from app.infrastructure.messaging.job_store import JobMetadataStore
from app.infrastructure.adapters.vector_adapter import QdrantAdapter
from app.core.security import verify_token
from app.workers.tasks import generate_report_task

# --- CONSTANTES DE SEGURIDAD PARA FILE UPLOADS (HI-07) ---
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB

MAGIC_BYTES_PDF = b"%PDF"
MAGIC_BYTES_PNG = b"\x89PNG\r\n\x1a\n"
MAGIC_BYTES_JPEG = b"\xff\xd8\xff"

# Instanciamos el Rate Limiter basado en la IP del cliente
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()
ASSETS_DIR = os.path.join(os.getcwd(), "static", "assets", "logos")

# ==============================================================================
# 1. REPORTES (Endpoints Principales)
# ==============================================================================
@router.post("/generate", status_code=status.HTTP_202_ACCEPTED, tags=["Reports"])
@limiter.limit("10/minute")
def generate_report(
    request: Request,
    payload: GenerateReportRequest, 
    job_store: JobMetadataStore = Depends(get_job_store),
    current_user: dict = Depends(verify_token)  
):
    """Encola la generación de un reporte PDF consultando la BD de ISA y la IA Local."""
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)
    
    generate_report_task.delay(
        evaluacion_id=payload.evaluacion_id,
        profile_name=payload.profile_name,
        institution_id=payload.institution_id,
        job_id=job_id,
        requester_id=current_user.get("sub"),
        requester_role=current_user.get("role")
    )
    
    return {
        "status": "accepted",
        "job_id": job_id, 
        "message": "Extracción y generación en segundo plano iniciada. Consulte el estado."
    }

@router.get("/status/{job_id}", tags=["Reports"])
@limiter.limit("60/minute")
def get_status(
    request: Request,
    job_id: str, 
    status_use_case: GetReportStatusUseCase = Depends(get_status_use_case),
    current_user: dict = Depends(verify_token) 
):
    """Consulta (Polling) el estado del reporte efímero."""
    result = status_use_case.execute(job_id)
    if result["status"] == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Job no encontrado en Redis.")
    return result

# ==============================================================================
# 2. REGLAS RAG (Gestión de Identidad Corporativa)
# ==============================================================================
@router.post("/rules/upload", tags=["Identity Rules"])
@limiter.limit("5/minute")
async def upload_pdf_rules(
    request: Request,
    profile_name: str = Form(..., description="Ej. Directivos_Nivel_A"),
    file: UploadFile = File(...),
    vector_db: QdrantAdapter = Depends(get_vector_db),
    current_user: dict = Depends(verify_token)  
):
    """Inyecta un PDF con las reglas de estilo en la Base de Datos Vectorial (Qdrant)."""
    
    # 1. Validación de Tamaño
    if file.size and file.size > MAX_PDF_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el límite permitido de 10MB.")

    # 2. Validación de Magic Bytes (Firma Binaria)
    header = await file.read(4)
    if not header.startswith(MAGIC_BYTES_PDF):
        raise HTTPException(status_code=415, detail="El archivo no es un PDF válido o está corrupto.")
    
    # Regresamos el cursor al inicio para que PdfReader pueda leerlo completo
    await file.seek(0)
    
    try:
        content = await file.read()
        reader = PdfReader(io.BytesIO(content))
        pdf_text = "".join([page.extract_text() or "" for page in reader.pages])
                
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="El PDF está vacío o es un documento escaneado (sin texto extraíble).")
            
        vector_db.upsert_rule(profile_name, pdf_text)
        
        return {"status": "success", "message": f"Reglas inyectadas en Qdrant para el perfil '{profile_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{profile_name}", tags=["Identity Rules"])
@limiter.limit("10/minute")
def delete_rules(
    request: Request,
    profile_name: str, 
    vector_db: QdrantAdapter = Depends(get_vector_db),
    current_user: dict = Depends(verify_token)  
):
    """Elimina las reglas de un perfil en Qdrant."""
    try:
        vector_db.delete_rule(profile_name)
        return {"status": "success", "message": f"Reglas de '{profile_name}' eliminadas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# 3. ASSETS (Logotipos e Imágenes)
# ==============================================================================
@router.post("/assets/logos/{institution_id}", status_code=status.HTTP_201_CREATED, tags=["Assets"])
@limiter.limit("10/minute")
async def upload_logo(
    request: Request,
    institution_id: str, 
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token) 
):
    """Sube un logo institucional (PNG/JPEG) validando su firma criptográfica."""
    
    # 1. Validación de Tamaño
    if file.size and file.size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el límite permitido de 5MB.")
    
    # 2. Validación de Magic Bytes (Firma Binaria)
    header = await file.read(8)
    is_png = header.startswith(MAGIC_BYTES_PNG)
    is_jpeg = header.startswith(MAGIC_BYTES_JPEG)
    
    if not (is_png or is_jpeg):
        raise HTTPException(status_code=415, detail="El archivo no es una imagen PNG o JPEG válida.")
    
    # Regresamos el cursor al inicio para guardarlo
    await file.seek(0)
    
    os.makedirs(ASSETS_DIR, exist_ok=True)
    file_path = os.path.join(ASSETS_DIR, f"{institution_id}.{'png' if is_png else 'jpg'}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": f"Logo para '{institution_id}' guardado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")

@router.delete("/assets/logos/{institution_id}", tags=["Assets"])
@limiter.limit("10/minute")
async def delete_logo(
    request: Request,
    institution_id: str,
    current_user: dict = Depends(verify_token)  
):
    # Buscamos si existe como PNG o JPG
    png_path = os.path.join(ASSETS_DIR, f"{institution_id}.png")
    jpg_path = os.path.join(ASSETS_DIR, f"{institution_id}.jpg")
    
    if os.path.exists(png_path):
        os.remove(png_path)
        return {"message": f"Logo '{institution_id}' eliminado."}
    elif os.path.exists(jpg_path):
        os.remove(jpg_path)
        return {"message": f"Logo '{institution_id}' eliminado."}
        
    raise HTTPException(status_code=404, detail="Logo no encontrado.")