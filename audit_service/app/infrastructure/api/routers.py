# app/infrastructure/api/routers.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status

from app.infrastructure.api.schemas import AuditLogCreateRequest, AuditLogResponse
from app.infrastructure.api.dependencies import (
    get_record_audit_use_case,
    get_audit_history_use_case,
    extract_client_ip,
    get_current_user_token
)
from app.application.use_cases.record_log import RecordAuditLogUseCase
from app.application.use_cases.get_history import GetAuditHistoryUseCase

router = APIRouter(prefix="/audit", tags=["Audit & Compliance"])

@router.post(
    "/", 
    response_model=AuditLogResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo evento de auditoría"
)
async def record_audit_log(
    request_data: AuditLogCreateRequest,
    client_ip: str = Depends(extract_client_ip),
    current_user: dict = Depends(get_current_user_token),
    use_case: RecordAuditLogUseCase = Depends(get_record_audit_use_case)
):
    """
    Punto de entrada inmutable. Registra qué hizo un usuario en el sistema.
    Aplica sanitización (OWASP) y minimización (LFPDPPP) automáticamente.
    """
    # Extraemos el actor_id de forma segura del JWT, NUNCA confiamos en el payload del cliente
    actor_id = UUID(current_user["sub"])

    # Delegamos al Caso de Uso
    log = await use_case.execute(
        actor_id=actor_id,
        action=request_data.action,
        resource_id=request_data.resource_id,
        resource_type=request_data.resource_type,
        ip_address=client_ip,
        details=request_data.details
    )
    
    return log


@router.get(
    "/resource/{resource_id}", 
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar historial de un recurso"
)
async def get_resource_history(
    resource_id: UUID,
    current_user: dict = Depends(get_current_user_token),
    use_case: GetAuditHistoryUseCase = Depends(get_audit_history_use_case)
):
    """
    Recupera todo el historial de cambios de un recurso específico (ej. una evaluación).
    Protegido por Role-Based Access Control (RBAC).
    """
    requester_role = current_user.get("role", "GUEST")
    
    # Delegamos al Caso de Uso, el cual validará si el rol tiene permisos
    history = await use_case.execute(
        resource_id=resource_id,
        requester_role=requester_role
    )
    
    return history