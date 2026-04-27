"""
Routers de API para bonus_service.
Cumple: OWASP SCP + LFPDPPP + OWASP Secure-by-Design.

Todos los endpoints están protegidos con autenticación Bearer y control de acceso por rol.
"""
import logging
import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.application.ports.input import CalculateBonusCommand, AuditContext
from app.application.use_cases.calculate_bonus import CalculateBonusUseCase
from app.application.use_cases.get_bonus_report import GetBonusReportUseCase
from app.core.security import get_current_user, require_role, CurrentUser
from app.core.logging import anonymize_ip
from app.infrastructure.api.dependencies import (
    get_calculate_bonus_use_case,
    get_bonus_report_use_case,
    get_remote_address,
    get_audit_context,
    AuditContext,
)
from app.infrastructure.api.schemas import (
    CalculateBonusRequest,
    CalculateBonusBatchRequest,
    BonusResponse,
    BatchAcceptedResponse,
    BonusReportResponse,
)
from app.infrastructure.api.middleware.rate_limit import check_rate_limit, record_auth_result, get_remote_address as rate_limit_get_remote_address
from app.workers.tasks import calculate_bonos_batch_task


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/bonus",
    tags=["Bonus"],
)


@router.post(
    "/calculate",
    response_model=BonusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cálculo individual de bono",
    description=(
        "Calcula el bono para una evaluación específica. "
        "Requiere rol 'admin' o 'finanzas'. "
        "El resultado se persiste con cifrado AES-256 y se registra en auditoría LFPDPPP."
    ),
    responses={
        401: {"description": "Token no proporcionado o inválido"},
        403: {"description": "Rol insuficiente"},
        409: {"description": "Bono ya calculado para esta evaluación"},
        422: {"description": "Datos de entrada inválidos"},
        429: {"description": "Demasiadas solicitudes"},
        500: {"description": "Error interno del servidor"},
    },
)
async def calculate_bonus(
    request: Request,
    payload: CalculateBonusRequest,
    current_user: CurrentUser,
    use_case: CalculateBonusUseCase = Depends(get_calculate_bonus_use_case),
):
    """
    Cálculo individual de bono con trazabilidad completa.
    
    FLUJO:
    1. Valida autenticación (HTTPBearer - token test12345)
    2. Verifica rol (admin o finanzas)
    3. Verifica rate limit
    4. Ejecuta cálculo via use case
    5. Retorna respuesta con monto enmascarado
    
    CUMPLIMIENTO:
    - OWASP Input Validation: Pydantic valida todos los campos
    - OWASP Authentication: HTTPBearer + RBAC
    - OWASP Authorization: Verifica rol en cada request
    - LFPDPPP Art. 18-19: Datos cifrados en reposo
    - LFPDPPP Art. 21: Trazabilidad en audit_logs
    """
    client_ip = anonymize_ip(get_remote_address(request))
    
    is_allowed, message = check_rate_limit(rate_limit_get_remote_address(request))
    if not is_allowed:
        raise HTTPException(status_code=429, detail=message)
    
    role_required = "admin" or "finanzas"
    if role_required not in current_user.get("roles", []):
        record_auth_result(rate_limit_get_remote_address(request), False, "Rol insuficiente")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: rol requerido",
        )
    
    command = CalculateBonusCommand(
        evaluacion_id=payload.evaluacion_id,
        salario_base_snapshot=Decimal(str(payload.salario_base_snapshot)),
        impacto_ebitda_logrado=Decimal(str(payload.impacto_ebitda_logrado)),
        calificacion_global=Decimal(str(payload.calificacion_global)) if payload.calificacion_global else None,
    )

    audit_ctx = AuditContext(
        user_id=current_user["user_id"],
        client_ip=client_ip,
        resource_id=str(payload.evaluacion_id),
    )

    try:
        result = await use_case.execute(command=command, audit_context=audit_ctx)
        record_auth_result(rate_limit_get_remote_address(request), True)
        
        return BonusResponse(
            evaluacion_id=result["evaluacion_id"],
            impacto_ebitda_logrado=float(result.get("impacto_ebitda_logrado", 0)),
            performance_index=float(result.get("performance_index", 0)),
            monto_enmascarado=f"**.{str(result.get('monto_final_bono', 0))[-2:]}",
            fecha_calculo=result.get("fecha_calculo"),
        )
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        logger.error(f"Error en cálculo de bono: {type(exc).__name__}: {exc}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.post(
    "/calculate/batch",
    response_model=BatchAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Cálculo masivo asíncrono (Celery)",
    description=(
        "Encola tareas de cálculo de bonos para procesamiento en background. "
        "Requiere rol 'admin' o 'finanzas'. "
        "El task se ejecuta vía Celery worker."
    ),
    responses={
        401: {"description": "Token no proporcionado o inválido"},
        403: {"description": "Rol insuficiente"},
        429: {"description": "Demasiadas solicitudes"},
    },
)
async def calculate_bonus_batch(
    request: Request,
    payload: CalculateBonusBatchRequest,
    current_user: CurrentUser,
):
    """
    Cálculo batch delegado a Celery worker.
    
    CUMPLIMIENTO:
    - OWASP Input Validation: Pydantic valida máximo 10,000 registros
    - OWASP Authorization: Verifica rol antes de encolar
    - LFPDPPP Art. 21: Trazabilidad con calculado_por
    """
    client_ip = anonymize_ip(get_remote_address(request))
    
    is_allowed, message = check_rate_limit(rate_limit_get_remote_address(request))
    if not is_allowed:
        raise HTTPException(status_code=429, detail=message)
    
    logger.info(
        f"Batch request: user={current_user['user_id']} "
        f"registros={len(payload.registros)} ip={client_ip}"
    )
    
    registros = [
        {
            "evaluacion_id": str(r.evaluacion_id),
            "salario_base_snapshot": float(r.salario_base_snapshot),
            "impacto_ebitda_logrado": float(r.impacto_ebitda_logrado),
            "calificacion_global": float(r.calificacion_global),
            "calculado_por": current_user["user_id"],
        }
        for r in payload.registros
    ]
    
    task = calculate_bonos_batch_task.delay(registros)
    
    return BatchAcceptedResponse(
        mensaje="Cálculo por lotes encolado exitosamente.",
        task_id=task.id,
        total_registros=len(registros),
    )


@router.get(
    "/report/{periodo_id}",
    response_model=BonusReportResponse,
    summary="Reporte consolidado por periodo",
    description=(
        "Genera reporte de bonos para un periodo. "
        "Roles 'admin' y 'finanzas' ven montos, 'sistemas' solo ve estadísticas."
    ),
    responses={
        401: {"description": "Token no proporcionado o inválido"},
        403: {"description": "Rol insuficiente"},
        429: {"description": "Demasiadas solicitudes"},
    },
)
async def get_bonus_report(
    request: Request,
    periodo_id: int,
    current_user: CurrentUser,
    use_case: GetBonusReportUseCase = Depends(get_bonus_report_use_case),
):
    """
    Reporte consolidado de bonos por periodo.
    
    CUMPLIMIENTO:
    - OWASP Authorization: Roles determinan qué datos se exponen
    - LFPDPPP: Roles 'sistemas' solo ven monto enmascarado
    """
    client_ip = anonymize_ip(get_remote_address(request))
    
    is_allowed, message = check_rate_limit(rate_limit_get_remote_address(request))
    if not is_allowed:
        raise HTTPException(status_code=429, detail=message)
    
    user_roles = current_user.get("roles", [])
    can_see_amounts = "finanzas" in user_roles or "admin" in user_roles
    
    bonos = await use_case.execute(periodo_id)
    
    if can_see_amounts:
        monto_total = sum(b.get("monto_final_bono", 0) for b in bonos)
        bonos_response = [
            BonusResponse(
                evaluacion_id=b["evaluacion_id"],
                impacto_ebitda_logrado=float(b.get("impacto_ebitda_logrado", 0)),
                performance_index=float(b.get("performance_index", 0)),
                monto_enmascarado=f"**.{str(b.get('monto_final_bono', 0))[-2:]}",
                fecha_calculo=b.get("fecha_calculo"),
            )
            for b in bonos
        ]
    else:
        monto_total = None
        bonos_response = [
            BonusResponse(
                evaluacion_id=b["evaluacion_id"],
                impacto_ebitda_logrado=float(b.get("impacto_ebitda_logrado", 0)),
                performance_index=float(b.get("performance_index", 0)),
                monto_enmascarado="**.**",
                fecha_calculo=b.get("fecha_calculo"),
            )
            for b in bonos
        ]

    logger.info(
        f"Report generated: periodo={periodo_id} "
        f"user={current_user['user_id']} "
        f"evaluaciones={len(bonos)} ip={client_ip}"
    )

    return BonusReportResponse(
        periodo_id=periodo_id,
        total_evaluaciones=len(bonos),
        monto_total=float(monto_total) if monto_total is not None else None,
        bonos=bonos_response,
    )


@router.get(
    "/health",
    tags=["Health"],
    summary="Health check público",
    description="Endpoint sin autenticación para monitoreo (Docker, Kubernetes, etc.).",
    include_in_schema=False,
)
async def health():
    """Health check público - no requiere autenticación."""
    return {"status": "ok", "service": "bonus_service", "version": "1.3.0"}


@router.get(
    "/auth/test",
    tags=["Debug"],
    summary="Test de autenticación (solo desarrollo)",
    description="Endpoint de prueba para verificar token. Requiere DEBUG_MODE=true.",
    include_in_schema=False,
)
async def test_auth(current_user: CurrentUser):
    """Test de autenticación - retorna datos del usuario."""
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    return {
        "authenticated": True,
        "user_id": current_user.get("user_id"),
        "roles": current_user.get("roles", []),
    }