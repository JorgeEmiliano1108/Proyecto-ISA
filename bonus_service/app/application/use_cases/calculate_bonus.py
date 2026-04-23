"""
Use Case: Cálculo individual de bono.
Cumple: OWASP Secure-by-Design Domain 2 (Business Logic) + LFPDPPP Art. 18-19.

Este use case orquesta:
1. Verificar si ya existe cálculo para la evaluación
2. Leer datos de evaluación (si se proporciona override de calificación)
3. Ejecutar cálculo matemático en el dominio (puro, sin frameworks)
4. Persistir resultado con cifrado AES-256
5. Registrar auditoría LFPDPPP
6. Publicar evento asíncrono vía Redis
"""
import uuid
import logging
from decimal import Decimal

from app.application.ports.input import CalculateBonusCommand, CalculateBonusInputPort, AuditContext
from app.application.ports.output import BonusRepositoryPort, EvaluacionReadRepositoryPort, AuditLogRepositoryPort
from app.domain import calculator
from app.domain.exceptions import BonusAlreadyCalculatedException, InvalidEBITDAException, InvalidCalificacionException


logger = logging.getLogger(__name__)


class CalculateBonusUseCase(CalculateBonusInputPort):
    """
    Caso de uso para cálculo de bono individual.
    
    CUMPLIMIENTO:
    - LFPDPPP Art. 18-19: Persistencia cifrada y auditoría
    - LFPDPPP Art. 21: Trazabilidad de quién calculó el bono
    - OWASP Secure-by-Design: Lógica de negocio en dominio puro
    
    FLUJO:
    1. Verificar duplicados → prevenido BonusAlreadyCalculatedException
    2. Leer evaluación (opcional con override de calificación)
    3. Calcular usando el módulo de dominio (puro Python + NumPy)
    4. Persistir en BD con campos cifrados (repository)
    5. Registrar en audit_logs (LFPDPPP)
    6. Publicar evento para listeners externos
    """

    def __init__(
        self,
        bonus_repo: BonusRepositoryPort,
        evaluacion_repo: EvaluacionReadRepositoryPort,
        audit_repo: AuditLogRepositoryPort,
        event_publisher,
    ):
        self._bonus_repo = bonus_repo
        self._evaluacion_repo = evaluacion_repo
        self._audit_repo = audit_repo
        self._publisher = event_publisher

    async def execute(
        self,
        command: CalculateBonusCommand,
        audit_context: AuditContext | None = None,
    ) -> dict:
        """
        Ejecuta el cálculo de bono con auditoría completa.
        
        Args:
            command: DTO con datos del cálculo
            audit_context: DTO con user_id y client_ip para trazabilidad LFPDPPP
            
        Returns:
            dict: Resultado del cálculo (serializado)
            
        Raises:
            BonusAlreadyCalculatedException: Si ya existe un bono para la evaluación
            InvalidEBITDAException: Si el EBITDA está fuera de rango válido
            InvalidCalificacionException: Si la calificación está fuera de 1.0-5.0
        """
        user_id = audit_context.user_id if audit_context else "system"
        client_ip = audit_context.client_ip if audit_context else None
        resource_id = audit_context.resource_id if audit_context else None

        try:
            existing = await self._bonus_repo.find_by_evaluacion(command.evaluacion_id)
            if existing:
                await self._audit_repo.log_action(
                    user_id=user_id,
                    action="calculate_bonus",
                    resource_id=str(command.evaluacion_id),
                    status="blocked",
                    detail="Intento de cálculo duplicado - bono ya existe",
                    client_ip=client_ip,
                )
                raise BonusAlreadyCalculatedException(command.evaluacion_id, "")

            evaluacion = await self._evaluacion_repo.get_by_id(command.evaluacion_id)
            
            calificacion = command.calificacion_global
            if calificacion is None and evaluacion:
                calificacion = Decimal(str(evaluacion.get("calificacion_global", 1.0)))

            if calificacion is None:
                raise InvalidCalificacionException(0.0)

            bonus_entity = calculator.calcular_bono_individual(
                evaluacion_id=command.evaluacion_id,
                salario_base_snapshot=float(command.salario_base_snapshot),
                impacto_ebitda_logrado=float(command.impacto_ebitda_logrado),
                calificacion_global=float(calificacion),
            )

            saved = await self._bonus_repo.save(
                bonus=bonus_entity,
                calculado_por=user_id,
            )

            await self._audit_repo.log_action(
                user_id=user_id,
                action="calculate_bonus",
                resource_id=str(command.evaluacion_id),
                status="success",
                detail=f"Bono calculado exitosamente - performance_index: {float(bonus_entity.performance_index):.2f}",
                client_ip=client_ip,
            )

            audit_payload = {
                "evaluacion_id": str(saved.evaluacion_id),
                "calculado_por": user_id,
                "performance_index": float(saved.performance_index),
                "impacto_ebitda_logrado": float(saved.impacto_ebitda_logrado),
                "monto_enmascarado": f"**.{str(saved.monto_final_bono)[-2:]}",
            }
            await self._publisher.publish("bonus.calculated", audit_payload)

            logger.info(
                f"Bono calculado: evaluacion={command.evaluacion_id} "
                f"calculado_por={user_id} performance_index={float(bonus_entity.performance_index):.2f}"
            )

            return saved.to_dict()

        except (InvalidEBITDAException, InvalidCalificacionException, BonusAlreadyCalculatedException):
            raise
        except Exception as exc:
            await self._audit_repo.log_action(
                user_id=user_id,
                action="calculate_bonus",
                resource_id=str(command.evaluacion_id),
                status="failure",
                detail=f"Error en cálculo: {type(exc).__name__}",
                client_ip=client_ip,
            )
            logger.error(f"Error en cálculo de bono: {exc}", exc_info=False)
            raise