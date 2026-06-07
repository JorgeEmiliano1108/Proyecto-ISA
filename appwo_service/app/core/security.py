# app/core/security.py
import re
import jwt
from typing import Optional
from fastapi import HTTPException, status

from app.core.config import settings

def _load_pem(value: str) -> str:
    """Convierte \\n literales a saltos de línea reales en una clave PEM."""
    return value.replace("\\n", "\n")

def verify_and_decode_jwt(token: str) -> str:
    """
    Valida el token JWT (RS256) contra la llave pública de ISA y extrae el actor_id.
    """
    if not token or token.lower() in ["invalid", "null", "bearer"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido, expirado o malformado."
        )

    public_key = _load_pem(settings.JWT_PUBLIC_KEY)
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado. Inicie sesión nuevamente."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o firma no reconocida."
        )

def sanitize_canvas_signature(signature_b64: str) -> str:
    """
    Limpia y valida que el payload de la firma electrónica sea un Base64 válido
    o un Hash esperado, evitando inyección de código o payloads maliciosos.
    """
    # Expresión regular básica para validar estructura Base64 (Data URI scheme)
    base64_pattern = re.compile(r"^data:image\/(png|jpeg|jpg);base64,[A-Za-z0-9+/=]+$")
    
    if not base64_pattern.match(signature_b64) and not signature_b64.isalnum():
        # Si no es un Base64 válido ni un hash alfanumérico, lo rechazamos
        raise ValueError("El formato de la firma electrónica es inválido o potencialmente peligroso.")
    
    return signature_b64