# app/infrastructure/api/routers.py
from fastapi import APIRouter, Depends, Request, HTTPException, status

# Importamos nuestros esquemas
from app.infrastructure.api.schemas import (
    ApproveEvaluationRequest, 
    RejectEvaluationRequest, 
    WorkflowActionResponse,
    ErrorResponse
)

# Importamos las excepciones de dominio y aplicación (para manejo seguro)
from app.domain.exceptions import DomainException
from app.core.exceptions import ApplicationException

# IMPORTANTE: Importamos los Puertos de Entrada (Interfaces) en lugar de la implementación
from app.application.ports.input import IApproveEvaluationUseCase, IRejectEvaluationUseCase, IStartReviewUseCase

from app.infrastructure.api.dependencies import (
    get_approve_use_case, 
    get_reject_use_case,
    get_current_actor_id,
    extract_client_ip,
    get_start_review_use_case
)

router = APIRouter(
    prefix="/api/v1/evaluations",
    tags=["Approval Workflow"]
)

@router.post(
    "/{evaluation_id}/approve", 
    response_model=WorkflowActionResponse, 
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def approve_evaluation_endpoint(
    evaluation_id: str,
    payload: ApproveEvaluationRequest,
    request: Request,
    actor_id: str = Depends(get_current_actor_id),
    use_case: IApproveEvaluationUseCase = Depends(get_approve_use_case), # <- Tipado de Interfaz
    ip_address: str = Depends(extract_client_ip)
):
    """
    Aprueba una evaluación en estado PENDING_APPROVAL.
    Requiere la firma electrónica del usuario autenticado.
    """
    try:
        # El controlador solo DELEGA al puerto de entrada
        result = await use_case.execute(
            evaluation_id=evaluation_id,
            actor_id=actor_id,
            signature_data=payload.signature_data,
            ip_address=ip_address
        )
        return WorkflowActionResponse(**result)
        
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")


@router.post(
    "/{evaluation_id}/reject", 
    response_model=WorkflowActionResponse, 
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def reject_evaluation_endpoint(
    evaluation_id: str,
    payload: RejectEvaluationRequest,
    request: Request,
    actor_id: str = Depends(get_current_actor_id),
    use_case: IRejectEvaluationUseCase = Depends(get_reject_use_case), # <- Tipado de Interfaz
    ip_address: str = Depends(extract_client_ip)
):
    """
    Rechaza una evaluación y la regresa al estado DRAFT.
    Exige un comentario de justificación.
    """
    try:
        result = await use_case.execute(
            evaluation_id=evaluation_id,
            actor_id=actor_id,
            justification=payload.justification,
            ip_address=ip_address
        )
        return WorkflowActionResponse(**result)
        
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")


@router.post(
    "/{evaluation_id}/review",
    response_model=WorkflowActionResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def start_review_endpoint(
    evaluation_id: str,
    request: Request,
    actor_id: str = Depends(get_current_actor_id),
    use_case: IStartReviewUseCase = Depends(get_start_review_use_case),
    ip_address: str = Depends(extract_client_ip)
) -> dict:
    """Pasa una evaluación de RECIBIDO a EN_REVISION."""
    try:
        result = await use_case.execute(
            evaluation_id=evaluation_id,
            actor_id=actor_id,
            ip_address=ip_address
        )
        return WorkflowActionResponse(**result)
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")