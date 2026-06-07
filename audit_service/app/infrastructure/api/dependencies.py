# app/infrastructure/api/dependencies.py
import jwt
from typing import AsyncGenerator
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.database import get_db_session
from app.infrastructure.database.repository import AuditRepository
from app.application.ports.output import EventPublisherPort
from app.application.use_cases.record_log import RecordAuditLogUseCase
from app.application.use_cases.get_history import GetAuditHistoryUseCase
from app.core.exceptions import UnauthorizedException
from app.core.config import settings
from app.infrastructure.messaging.publisher import RedisEventPublisher

security = HTTPBearer()


def _load_pem(value: str) -> str:
    """Convierte \\n literales a saltos de línea reales en una clave PEM."""
    return value.replace("\\n", "\n")


# Seguridad (Authentication & Proxy Support)


async def extract_client_ip(request: Request) -> str:
    """
    Extrae la IP real del cliente. Vital para auditoría LFPDPPP.
    Considera que el servicio está detrás de un API Gateway (Kong/Traefik).
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"

async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Valida el JWT RS256 contra la llave pública de ISA y extrae actor_id + rol.
    """
    token = credentials.credentials
    if not token:
        raise UnauthorizedException(internal_message="Token no proporcionado.")

    public_key = _load_pem(settings.JWT_PUBLIC_KEY)
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return {
            "sub": payload.get("user_id"),
            "role": payload.get("rol_nombre", "usuario")
        }
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(internal_message="Token expirado.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(internal_message="Token inválido o firma no reconocida.")


# Ensamblaje de Casos de Uso (Dependency Injection)

def get_audit_repository(session: AsyncSession = Depends(get_db_session)) -> AuditRepository:
    return AuditRepository(session=session)

def get_event_publisher() -> EventPublisherPort:
    # 🚀 CAMBIO CRÍTICO: Ahora inyectamos el publicador real conectado a Redis
    return RedisEventPublisher()

def get_record_audit_use_case(
    repository: AuditRepository = Depends(get_audit_repository),
    publisher: EventPublisherPort = Depends(get_event_publisher)
) -> RecordAuditLogUseCase:
    return RecordAuditLogUseCase(repository=repository, publisher=publisher)

def get_audit_history_use_case(
    repository: AuditRepository = Depends(get_audit_repository)
) -> GetAuditHistoryUseCase:
    return GetAuditHistoryUseCase(repository=repository)