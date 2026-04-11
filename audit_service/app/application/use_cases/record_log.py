# app/application/use_cases/record_log.py
from typing import Any, Dict, Optional
from uuid import UUID

from app.domain.entities import AuditLog
from app.application.ports.input import RecordAuditLogInputPort
from app.application.ports.output import AuditRepositoryPort, EventPublisherPort
from app.core.security import sanitize_payload, mask_pii, generate_log_signature
from app.core.config import settings

class RecordAuditLogUseCase(RecordAuditLogInputPort):  
    """
    Caso de Uso: Registrar una nueva acción de auditoría.
    Implementa el puerto de entrada RecordAuditLogInputPort.
    Orquesta la sanitización, validación, firma criptográfica y persistencia.
    """
    
    def __init__(
        self, 
        repository: AuditRepositoryPort, 
        publisher: EventPublisherPort
    ):
        # Inyección de Dependencias (DIP - Principio de Inversión de Dependencias)
        self.repository = repository
        self.publisher = publisher

    async def execute(
        self, 
        actor_id: UUID, 
        action: str, 
        resource_type: str, 
        ip_address: str, 
        details: Dict[str, Any],
        resource_id: Optional[UUID] = None
    ) -> AuditLog:
        
        # Sanitización y Enmascaramiento de datos de entrada
        # Evitamos XSS y minimizamos la exposición de PII en textos libres.
        safe_details = sanitize_payload(details)
        
        # Si hay un campo de 'justification' o 'comments', aplicamos masking de correos/nombres
        if "justification" in safe_details and isinstance(safe_details["justification"], str):
            safe_details["justification"] = mask_pii(safe_details["justification"])

        # Dominio: Instanciamos la entidad (Aquí se validan reglas de negocio e inmutabilidad)
        # Si la acción no es válida, lanzará una InvalidAuditLogActionException
        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            resource_id=resource_id,
            resource_type=resource_type,
            ip_address=ip_address,
            details=safe_details
        )

        # Firma Criptográfica (Tamper-Evidence)
        # Extraemos el diccionario determinista y generamos el HMAC
        data_to_sign = audit_log.to_dict_for_signing()
        signature = generate_log_signature(
            log_data=data_to_sign, 
            secret_key=settings.SECRET_KEY.get_secret_value()
        )
        
        # Creamos la copia inmutable con la firma incluida
        signed_log = audit_log.with_signature(signature)

        # Infraestructura: Persistencia
        saved_log = await self.repository.save(signed_log)

        # Event-Driven: Notificamos asíncronamente 
        # Esto no bloquea la respuesta principal si falla el broker
        try:
            await self.publisher.publish_audit_event(
                event_name=f"audit.{action.lower()}", 
                log=saved_log
            )
        except Exception as e:
            # Aquí idealmente usaríamos el logger de la aplicación para registrar 
            # que el broker de mensajería falló, pero NO detenemos la transacción.
            # logger.warning(f"No se pudo publicar el evento de auditoría: {e}")
            pass

        return saved_log