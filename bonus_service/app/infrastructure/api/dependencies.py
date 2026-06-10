"""
Dependencias de inyección para la capa de infraestructura.
Cumple: OWASP SCP - Dependency Injection best practices.
"""
from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.calculate_logro import CalculateLogroUseCase
from app.application.use_cases.get_logro_report import GetLogroReportUseCase
from app.application.use_cases.get_calculos_list import GetCalculosListUseCase
from app.core.logging import anonymize_ip
from app.infrastructure.database.database import get_write_session as _get_write_session, get_read_session as _get_read_session
from app.infrastructure.database.repository import (
    SQLCalculoLogroRepository,
    SQLEvaluacionReadRepository,
    SQLAuditLogRepository,
)
from app.infrastructure.messaging.publisher import event_publisher


def get_remote_address(request: Request) -> Optional[str]:
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


def get_logro_repository(session: AsyncSession = Depends(get_write_session)) -> SQLCalculoLogroRepository:
    """Repositorio de cálculos de logro con cifrado AES-256."""
    return SQLCalculoLogroRepository(session)


def get_evaluacion_repository(session: AsyncSession = Depends(get_read_session)) -> SQLEvaluacionReadRepository:
    """Repositorio de solo lectura para evaluaciones."""
    return SQLEvaluacionReadRepository(session)


def get_audit_repository(session: AsyncSession = Depends(get_write_session)) -> SQLAuditLogRepository:
    """Repositorio de auditoría para trazabilidad LFPDPPP."""
    return SQLAuditLogRepository(session)


def get_calculate_logro_use_case(
    logro_repo: SQLCalculoLogroRepository = Depends(get_logro_repository),
    eval_repo: SQLEvaluacionReadRepository = Depends(get_evaluacion_repository),
    audit_repo: SQLAuditLogRepository = Depends(get_audit_repository),
) -> CalculateLogroUseCase:
    """
    Instancia del UseCase de cálculo de logro con auditoría habilitada.
    LFPDPPP: La trazabilidad se pasa desde el router en cada request.
    """
    return CalculateLogroUseCase(
        logro_repo=logro_repo,
        evaluacion_repo=eval_repo,
        audit_repo=audit_repo,
        event_publisher=event_publisher,
    )


def get_logro_report_use_case(
    logro_repo: SQLCalculoLogroRepository = Depends(get_logro_repository),
) -> GetLogroReportUseCase:
    """Instancia del UseCase de reporte de logros."""
    return GetLogroReportUseCase(logro_repo=logro_repo)


def get_calculos_list_use_case(
    logro_repo: SQLCalculoLogroRepository = Depends(get_logro_repository),
) -> GetCalculosListUseCase:
    """Instancia del UseCase de listado paginado de cálculos."""
    return GetCalculosListUseCase(logro_repo=logro_repo)


def get_audit_context(
    request: Request,
    current_user: dict,
    resource_id: Optional[str] = None,
) -> dict:
    """
    Construye el contexto de auditoría para LFPDPPP compliance.
    """
    return {
        "user_id": current_user.get("user_id", "unknown"),
        "client_ip": anonymize_ip(get_remote_address(request)),
        "resource_id": resource_id,
    }
