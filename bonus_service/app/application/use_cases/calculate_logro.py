"""
Use Case: Cálculo individual de porcentaje de logro.
Cumple: OWASP Secure-by-Design + LFPDPPP Art. 18-19.
"""
import uuid
import logging

from app.application.ports.input import (
    CalculateLogroCommand,
    CalculateLogroInputPort,
    AuditContext,
)
from app.application.ports.output import (
    LogroRepositoryPort,
    EvaluacionReadRepositoryPort,
    AuditLogRepositoryPort,
)
from app.domain import calculator
from app.domain.exceptions import InvalidCalificacionException, BonusAlreadyCalculatedException


logger = logging.getLogger(__name__)


class CalculateLogroUseCase(CalculateLogroInputPort):
    """
    Caso de uso para cálculo de porcentaje de logro individual.

    CUMPLIMIENTO:
    - LFPDPPP Art. 18-19: Persistencia cifrada y auditoría
    - LFPDPPP Art. 21: Trazabilidad de quién calculó el logro
    - OWASP Secure-by-Design: Lógica de negocio en dominio puro
    """

    def __init__(
        self,
        logro_repo: LogroRepositoryPort,
        evaluacion_repo: EvaluacionReadRepositoryPort,
        audit_repo: AuditLogRepositoryPort,
        event_publisher,
    ):
        self._logro_repo = logro_repo
        self._evaluacion_repo = evaluacion_repo
        self._audit_repo = audit_repo
        self._publisher = event_publisher

    async def execute(self, command: CalculateLogroCommand, audit_context: AuditContext = None) -> dict:
        """
        Ejecuta el cálculo de porcentaje de logro con auditoría completa.

        Args:
            command: DTO con evaluacion_id y calificacion_global
            audit_context: DTO con user_id y client_ip (trazabilidad LFPDPPP)

        Returns:
            dict: Resultado del cálculo (evaluacion_id, calificacion_global, porcentaje_logro, fecha_calculo)

        Raises:
            BonusAlreadyCalculatedException: Si ya existe un logro para la evaluación
            InvalidCalificacionException: Si la calificación está fuera de 1.0-5.0
        """
        user_id = audit_context.get("user_id") if isinstance(audit_context, dict) else (audit_context.user_id if audit_context else "system")
        client_ip = audit_context.get("client_ip") if isinstance(audit_context, dict) else getattr(audit_context, 'client_ip', None)

        try:
            existing = await self._logro_repo.find_by_evaluacion(command.evaluacion_id)
            if existing:
                await self._audit_repo.log_action(
                    user_id=user_id,
                    action="calculate_logro",
                    resource_id=str(command.evaluacion_id),
                    status="blocked",
                    detail="Intento de cálculo duplicado - logro ya existe",
                    client_ip=client_ip,
                )
                raise BonusAlreadyCalculatedException(command.evaluacion_id, "")

            # Cálculo matemático en el dominio (puro)
            logro_entity = calculator.calcular_logro_individual(
                evaluacion_id=command.evaluacion_id,
                calificacion_global=command.calificacion_global,
            )

            # Persistir resultado con cifrado de datos sensibles
            saved = await self._logro_repo.save(
                calculo=logro_entity,
                calculado_por=user_id,
            )

            # Auditoría LFPDPPP
            await self._audit_repo.log_action(
                user_id=user_id,
                action="calculate_logro",
                resource_id=str(command.evaluacion_id),
                status="success",
                detail=f"Porcentaje de logro calculado: {logro_entity.porcentaje_logro}%",
                client_ip=client_ip,
            )

            # Publicar evento asíncrono (sin datos sensibles — solo metadatos)
            await self._publisher.publish("logro.calculated", {
                "evaluacion_id": str(saved.evaluacion_id),
                "calculado_por": user_id,
                "porcentaje_logro": saved.porcentaje_logro,
            })

            logger.info(
                f"Logro calculado: evaluacion={command.evaluacion_id} "
                f"calculado_por={user_id} porcentaje_logro={logro_entity.porcentaje_logro}%"
            )

            return {
                "evaluacion_id": str(saved.evaluacion_id),
                "calificacion_global": saved.calificacion_global,
                "porcentaje_logro": saved.porcentaje_logro,
                "fecha_calculo": saved.fecha_calculo.isoformat(),
            }

        except InvalidCalificacionException:
            raise
        except Exception as exc:
            await self._audit_repo.log_action(
                user_id=user_id,
                action="calculate_logro",
                resource_id=str(command.evaluacion_id),
                status="failure",
                detail=f"Error en cálculo: {type(exc).__name__}",
                client_ip=client_ip,
            )
            logger.error(f"Error en cálculo de logro: {exc}", exc_info=False)
            raise
