# app/core/exceptions.py

class ApplicationException(Exception):
    """
    Clase base para errores que ocurren en la capa de Aplicación o Infraestructura,
    ajenos a las reglas puras del Dominio (ej. Fallo al conectar con Active Directory).
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundException(ApplicationException):
    """Lanzada cuando un registro no existe en la base de datos."""
    def __init__(self, resource_name: str, identifier: str):
        super().__init__(
            message=f"No se encontró el recurso '{resource_name}' con identificador '{identifier}'.",
            status_code=404
        )

class ExternalServiceException(ApplicationException):
    """Lanzada cuando un microservicio externo (ej. User Service) no responde."""
    def __init__(self, service_name: str, detail: str):
        super().__init__(
            message=f"Fallo en la comunicación con el servicio externo [{service_name}]: {detail}",
            status_code=502
        )