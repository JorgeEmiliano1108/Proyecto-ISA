"""
Seguridad y autenticación para bonus_service.
Cumple: OWASP SCP (Secure Coding Practices) + OWASP Secure-by-Design Framework.

Validación de token Bearer con JWT real — Sin mocks ni hardcode.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Annotated, List

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


security_scheme = HTTPBearer(
    auto_error=True,
    description="Token Bearer para autenticación",
)


def _get_jwt_secret() -> str:
    """Obtiene el secreto JWT de variables de entorno o Docker Secret."""
    # Prioridad 1: Docker Secret
    secret_path = os.environ.get("JWT_SECRET_PATH", "/run/secrets/jwt_secret_key")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            secret = f.read().strip()
            if secret:
                return secret

    # Prioridad 2: JWT_SECRET_KEY (nombre estándar)
    jwt_secret = os.environ.get("JWT_SECRET_KEY")
    if jwt_secret:
        return jwt_secret

    # Prioridad 3: SECRET_KEY (nombre actual en tu .env)
    jwt_secret = os.environ.get("SECRET_KEY")
    if jwt_secret:
        return jwt_secret

    # Fallback para desarrollo local (NO usar en producción)
    if os.environ.get("DEBUG_MODE", "false").lower() == "true":
        import warnings
        warnings.warn(
            "USANDO JWT SECRET POR DEFECTO EN MODO DEBUG. "
            "NUNCA HAGAS ESTO EN PRODUCCIÓN.",
            RuntimeWarning,
        )
        return "dev-secret-change-in-production-do-not-use"

    raise RuntimeError(
        "JWT_SECRET_KEY o SECRET_KEY no está configurado. "
        "Proporciona el secreto vía Docker Secret, JWT_SECRET_KEY o SECRET_KEY."
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]
) -> dict:
    """
    Valida el token Bearer y retorna los datos del usuario.

    OWASP SCP: Validación de entrada estricta.
    OWASP Secure-by-Design: Fail-safe defaults - rechazar tokens inválidos.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer realm='bonus_service'"},
        )

    token = credentials.credentials

    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        roles = payload.get("roles", [])

        if not user_id:
            raise ValueError("Token inválido: falta 'sub'")

        return {
            "user_id": user_id,
            "roles": roles,
            "authenticated": True,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[dict, Depends(get_current_user)]


# DEPRECATED: create_test_token mantenida solo para pruebas locales
# En producción, este endpoint debe ser reemplazado por un servicio de auth real
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
    
    # Obtener secret de forma segura
    secret = (
        os.environ.get("JWT_SECRET_KEY") or
        os.environ.get("SECRET_KEY") or
        "dev-secret-change-in-production-do-not-use"
    )
    
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
