"""app/core/security.py

Módulo de seguridad para validar la autenticación inter-servicios.
Asegura que solo usuarios autenticados del corporativo puedan generar PDFs,
utilizando validación asimétrica (RS256) y listas de revocación en Redis.
"""

import jwt
import redis
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

logger = logging.getLogger("ms_reports.security")
security = HTTPBearer()

# Inicializamos el cliente de Redis para consultar la Lista de Revocación (Denylist)
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Fallo al conectar con Redis para seguridad: {e}")
    redis_client = None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependencia de FastAPI. Extrae el Bearer Token, lo valida criptográficamente 
    usando la Llave Pública (RS256) y comprueba que no haya sido revocado.
    """
    token = credentials.credentials
    try:
        # Decodificamos el token exigiendo claims mínimos obligatorios
        payload = jwt.decode(
            token, 
            settings.JWT_PUBLIC_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]} # sub (Subject/User ID), exp (Expiration)
        )
        
        # Validación contra Lista de Revocación en Redis (Para soporte de Logout)
        jti = payload.get("jti") # JWT ID
        if jti and redis_client:
            if redis_client.exists(f"REVOKED_TOKENS:{jti}"):
                logger.warning(f"Intento de acceso con token revocado (JTI: {jti}).")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="El token ha sido revocado (Sesión cerrada). Inicie sesión de nuevo.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        return payload
    
    except jwt.ExpiredSignatureError:
        logger.warning("Intento de acceso con token expirado.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de sesión ha expirado. Por favor, inicia sesión de nuevo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"Intento de acceso con token malformado o firma inválida: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas o firma no reconocida.",
            headers={"WWW-Authenticate": "Bearer"},
        )