"""
Entidades del dominio — modelo de datos puro sin dependencias de frameworks.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CalculoLogro:
    """
    Entidad inmutable que representa el cálculo de porcentaje de logro.
    Alineada al dominio: Solo calificación y porcentaje.
    """
    evaluacion_id: uuid.UUID          # FK hacia evaluaciones.id
    calificacion_global: float         # 1.0 – 5.0 (input del evaluador)
    porcentaje_logro: float            # Resultado del cálculo (20% - 100%)
    fecha_calculo: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Serializa la entidad a diccionario estándar."""
        return {
            "evaluacion_id": str(self.evaluacion_id),
            "calificacion_global": self.calificacion_global,
            "porcentaje_logro": self.porcentaje_logro,
            "fecha_calculo": self.fecha_calculo.isoformat(),
        }
