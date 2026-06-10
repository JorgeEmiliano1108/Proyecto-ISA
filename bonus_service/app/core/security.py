"""
Seguridad y autenticación para bonus_service.
Cumple: OWASP SCP (Secure Coding Practices) + OWASP Secure-by-Design Framework.

Validación de token Bearer con JWT RS256 asimétrico — Django firma, Bonus valida.
"""
import uuid
from datetime import datetime, timedelta
from typing import Annotated, List, Optional

import jwt
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


security_scheme = HTTPBearer(
    auto_error=True,
    description="Token Bearer para autenticación",
)


def _get_jwt_public_key() -> str:
    """Obtiene la clave pública JWT desde settings (variable de entorno JWT_PUBLIC_KEY)."""
    return settings.JWT_PUBLIC_KEY


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]
) -> dict:
    """
    Valida el token Bearer RS256 y retorna los datos del usuario.

    OWASP SCP: Validación de entrada estricta.
    OWASP Secure-by-Design: Fail-safe defaults - rechazar tokens inválidos.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"get_current_user called with credentials: {credentials}")
    
    if credentials is None:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer realm='bonus_service'"},
        )

    token = credentials.credentials

    if not token or not isinstance(token, str):
        logger.warning(f"Invalid token: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        logger.info("Attempting to decode token with RS256")
        payload = jwt.decode(
            token,
            _get_jwt_public_key(),
            algorithms=["RS256"],
        )
        logger.info(f"Token decoded successfully: {payload}")
        user_id = payload.get("sub")
        roles = payload.get("roles", [])

        if not user_id:
            logger.warning("Token missing 'sub' claim")
            raise ValueError("Token inválido: falta 'sub'")

        return {
            "user_id": user_id,
            "roles": roles,
            "authenticated": True,
        }
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[dict, Depends(get_current_user)]


# Dependency para verificar que el token pertenece a un servicio interno (Django)
async def require_internal_service(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """
    Dependency que verifica que el token pertenece a un servicio interno autorizado.
    Requiere que el token tenga el rol 'internal-service'.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"require_internal_service called with user: {current_user}")
    user_roles = current_user.get("roles", [])
    logger.info(f"User roles: {user_roles}")
    if "internal-service" not in user_roles:
        logger.warning(f"Missing internal-service role, roles: {user_roles}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol 'internal-service'",
        )
    return current_user


# Dependency legacy para compatibilidad temporal (API Key)
async def verify_internal_api_key(
    x_internal_api_key: Annotated[Optional[str], Header(alias="X-Internal-Api-Key")] = None
) -> str:
    """
    ⚠️ DEPRECATED - Valida la API Key interna para comunicación entre microservicios.
    
    Uso: Django envía header 'X-Internal-Api-Key: isa_internal_key_2026'
    Migración: Usar JWT con rol 'internal-service' en su lugar.
    """
    import warnings
    warnings.warn(
        "verify_internal_api_key está DEPRECADO. Usar JWT con rol 'internal-service'.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if not x_internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key interna requerida",
            headers={"WWW-Authenticate": "InternalApiKey"},
        )
    
    if x_internal_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key interna inválida",
        )
    
    return x_internal_api_key


# DEPRECATED: create_test_token mantenida solo para pruebas locales
def create_test_token(user_id: str, roles: List[str], expires_hours: int = 24) -> str:
    """
    ⚠️ DEPRECATED - SOLO PARA PRUEBAS LOCALES
    
    Genera un token JWT para testing. En producción, NO debe usarse.
    El endpoint /auth/login en routers.py usa esta función temporalmente.
    """
    import warnings
    warnings.warn(
        "create_test_token está DEPRECADADO. Usar solo en pruebas locales.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Usar JWT_SECRET_KEY de settings (legacy HS256)
    secret = settings.JWT_SECRET_KEY
    
    # Si no se especifican roles, usar admin por defecto
    if not roles:
        roles = ["admin"]
    
    expires_delta = timedelta(hours=expires_hours)
    now = datetime.utcnow()
    exp = now + expires_delta
    
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": exp,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def require_role(*allowed_roles: str):
    """
    Decorador para proteger endpoints por rol.

    OWASP SCP: Authorization - Verificar permisos en cada acceso.
    """
    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: rol requerido",
            )
        return current_user

    return Depends(_checker)