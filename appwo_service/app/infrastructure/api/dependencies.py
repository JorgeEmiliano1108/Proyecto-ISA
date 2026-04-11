# app/infrastructure/api/dependencies.py
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

# Importar la sesión de DB
from app.infrastructure.database.database import get_db_session 

# Importar los Repositorios y Adaptadores
from app.infrastructure.database.repository import ApprovalRepository
from app.infrastructure.messaging.publisher import RedisEventPublisher
from app.infrastructure.clients.user_service import UserServiceClient

# IMPORTANTE: Importamos el Mock Client que acabas de crear
from app.infrastructure.clients.mock_user_service import MockUserServiceClient 

# Importamos Puertos de Entrada y Casos de Uso
from app.application.ports.input import IApproveEvaluationUseCase, IRejectEvaluationUseCase
from app.application.use_cases.approve_evaluation import ApproveEvaluationUseCase
from app.application.use_cases.reject_evaluation import RejectEvaluationUseCase

# Importar el módulo de seguridad del Core y las Configuraciones
from app.core.security import verify_and_decode_jwt
from app.core.config import settings



# Seguridad


security = HTTPBearer()

async def extract_client_ip(request: Request) -> str:
    """Extrae la IP real del cliente para trazabilidad LFPDPPP."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"

async def get_current_actor_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Delega la validación y extracción del JWT al core de seguridad.
    """
    return verify_and_decode_jwt(credentials.credentials)



# Instancias Singleton (Servicios Externos)


# Publicador de Redis instanciado usando las variables globales seguras
redis_publisher = RedisEventPublisher(redis_url=settings.REDIS_URL)

# INTERRUPTOR INTELIGENTE (Patrón Estrategia)
if settings.USE_MOCK_SERVICES:
    print("🔧 Iniciando API con servicios externos en modo MOCK...")
    user_client = MockUserServiceClient()
else:
    print("🚀 Iniciando API con servicios externos REALES...")
    user_client = UserServiceClient(base_url=settings.USER_SERVICE_URL)



# Ensamblaje de Casos de Uso (DI Factory)


def get_approval_repository(session: AsyncSession = Depends(get_db_session)) -> ApprovalRepository:
    """Crea un repositorio fresco asociado a la transacción actual."""
    return ApprovalRepository(session=session)

def get_approve_use_case(
    repository: ApprovalRepository = Depends(get_approval_repository)
) -> IApproveEvaluationUseCase:
    return ApproveEvaluationUseCase(
        repository=repository,
        event_publisher=redis_publisher,
        user_service=user_client
    )

def get_reject_use_case(
    repository: ApprovalRepository = Depends(get_approval_repository)
) -> IRejectEvaluationUseCase:
    return RejectEvaluationUseCase(
        repository=repository,
        event_publisher=redis_publisher,
        user_service=user_client
    )