# app/domain/exceptions.py

class DomainException(Exception):
    """Excepción base para violaciones de reglas de negocio en el Dominio."""
    pass

class InvalidAuditLogActionException(DomainException):
    """Se lanza cuando se intenta registrar una acción no permitida o desconocida."""
    def __init__(self, action: str):
        self.action = action
        super().__init__(f"La acción '{action}' no es válida para la auditoría.")

class MissingAuditDataException(DomainException):
    """Se lanza cuando faltan datos críticos exigidos por la LFPDPPP."""
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"El campo obligatorio para auditoría '{field}' está ausente.")

class ImmutableLogModificationException(DomainException):
    """Se lanza si se intenta modificar un log después de haber sido creado."""
    def __init__(self):
        super().__init__("Violación de inmutabilidad: Los registros de auditoría son de solo lectura.")