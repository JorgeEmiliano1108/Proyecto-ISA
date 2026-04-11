# app/core/security.py
import re
from typing import Optional
from fastapi import HTTPException, status

def verify_and_decode_jwt(token: str) -> str:
    """
    Valida el token JWT y extrae el actor_id.
    En producción, aquí integrarías la librería `PyJWT` usando la llave pública de ISA.
    """
    if not token or token.lower() in ["invalid", "null", "bearer"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido, expirado o malformado."
        )
    
    # Mock para desarrollo: Extraemos el ID del usuario del token simulado
    # Ejemplo real: payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    # return payload["sub"]
    
    return "uuid-del-gerente-o-director"

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