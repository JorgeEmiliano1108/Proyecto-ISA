"""
Dependencias de inyección para la capa de infraestructura.
Cumple: OWASP SCP - Dependency Injection best practices.
"""
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.calculate_bonus import CalculateBonusUseCase
from app.application.use_cases.get_bonus_report import GetBonusReportUseCase
from app.core.security import get_current_user, CurrentUser
from app.core.logging import anonymize_ip
from app.infrastructure.database.database import get_write_session as _get_write_session, get_read_session as _get_read_session
from app.infrastructure.database.repository import (
    SQLBonusRepository,
    SQLEvaluacionReadRepository,
    SQLAuditLogRepository,
)
from app.infrastructure.messaging.publisher import event_publisher


def get_remote_address(request: Request) -> str | None:
    """Obtiene IP del cliente considerando proxies (X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesión de escritura para operaciones de base de datos."""
    async for session in _get_write_session():
        yield session


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesión de lectura para operaciones de base de datos."""
    async for session in _get_read_session():
        yield session


def get_bonus_repository(session: AsyncSession = Depends(get_write_session)) -> SQLBonusRepository:
    """Repositorio de bonos con cifrado AES-256."""
    return SQLBonusRepository(session)


def get_evaluacion_repository(session: AsyncSession = Depends(get_read_session)) -> SQLEvaluacionReadRepository:
    """Repositorio de solo lectura para evaluaciones."""
    return SQLEvaluacionReadRepository(session)


def get_audit_repository(session: AsyncSession = Depends(get_write_session)) -> SQLAuditLogRepository:
    """Repositorio de auditoría para trazabilidad LFPDPPP."""
    return SQLAuditLogRepository(session)


def get_calculate_bonus_use_case(
    bonus_repo: SQLBonusRepository = Depends(get_bonus_repository),
    eval_repo: SQLEvaluacionReadRepository = Depends(get_evaluacion_repository),
    audit_repo: SQLAuditLogRepository = Depends(get_audit_repository),
) -> CalculateBonusUseCase:
    """
    Instancia del UseCase de cálculo de bono con auditoría habilitada.
    LFPDPPP: La trazabilidad se pasa desde el router via get_current_user.
    """
    return CalculateBonusUseCase(
        bonus_repo=bonus_repo,
        evaluacion_repo=eval_repo,
        audit_repo=audit_repo,
        event_publisher=event_publisher,
    )


def get_bonus_report_use_case(
    bonus_repo: SQLBonusRepository = Depends(get_bonus_repository),
) -> GetBonusReportUseCase:
    """Instancia del UseCase de reporte de bonos."""
    return GetBonusReportUseCase(bonus_repo=bonus_repo)


def get_audit_context(
    request: Request,
    current_user: CurrentUser,
    resource_id: str | None = None,
) -> dict:
    """
    Construye el contexto de auditoría paraLFPDPPP compliance.
    
    Args:
        request: Request de FastAPI para extraer IP.
        current_user: Usuario autenticado del token.
        resource_id: ID del recurso afectado (opcional).
        
    Returns:
        dict: Contexto de auditoría con user_id y client_ip anonimizada.
    """
    client_ip = anonymize_ip(get_remote_address(request))
    
    return {
        "user_id": current_user.get("user_id", "unknown"),
        "client_ip": client_ip,
        "resource_id": resource_id,
    }


AuditContext = Annotated[dict, Depends(get_audit_context)]