# app/domain/exceptions.py

class DomainException(Exception):
    """
    Clase base para todas las excepciones puras de negocio.
    Cualquier error que herede de esta clase se traduce en un error de regla de negocio
    y no en un error de sistema (HTTP 400 o 403, no 500).
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidTransitionException(DomainException):
    """Lanzada cuando se intenta un salto de estado no permitido (ej. de DRAFT a APPROVED)."""
    pass


class UnauthorizedApprovalException(DomainException):
    """Lanzada cuando un rol intenta aprobar fuera de su jerarquía o turno."""
    pass


class MissingJustificationException(DomainException):
    """Lanzada cuando se intenta rechazar sin proporcionar un comentario de retroalimentación."""
    pass


class MissingSignatureException(DomainException):
    """Lanzada cuando se intenta aprobar sin proporcionar el payload de la firma en canvas (Base64)."""
    pass