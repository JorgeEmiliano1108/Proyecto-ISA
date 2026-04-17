"""app/application/ports/input.py

Puertos de Entrada (Primary Ports).
Definen las interfaces que el mundo exterior (API, CLI, Workers) debe usar 
para interactuar con la lógica de negocio del microservicio de reportes.
"""

from abc import ABC, abstractmethod

class GenerateReportInputPort(ABC):
    """Interfaz para el caso de uso de generación de reportes."""
    
    @abstractmethod
    def run(self, evaluacion_id: str, profile_name: str, institution_id: str, job_id: str) -> None:
        """
        Inicia el proceso asíncrono de generación de un reporte.
        """
        pass

class GetReportStatusInputPort(ABC):
    """Interfaz para la consulta de estado de un reporte en proceso."""
    
    @abstractmethod
    def execute(self, job_id: str) -> dict:
        """
        Recupera el estado actual y el resultado (si existe) de un reporte.
        """
        pass