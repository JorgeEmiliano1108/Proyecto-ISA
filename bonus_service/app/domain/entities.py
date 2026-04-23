import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Evaluacion:
    """
    Entidad inmutable de entrada. 
    Representa los datos extraídos de la base de datos (u otra fuente) 
    necesarios para ejecutar el cálculo financiero.
    """
    id: uuid.UUID
    empleado_id: int
    periodo: str
    salario_base: Decimal
    calificacion_global: Decimal
    impacto_ebitda_logrado: Decimal


@dataclass(frozen=True)
class BonusCalculation:
    """
    Entidad inmutable que representa el resultado matemático de un cálculo de bono.
    Alineada al esquema real: tabla 'bonos' referencia a 'evaluaciones' por UUID.
    Sin dependencias de frameworks externos — 100% Python puro.
    """
    evaluacion_id: uuid.UUID          # FK hacia evaluaciones.id
    salario_base_snapshot: Decimal    # Salario al momento del cálculo
    impacto_ebitda_logrado: Decimal   # % EBITDA corporativo logrado
    performance_index: Decimal        # Índice derivado de calificacion_global
    monto_final_bono: Decimal         # Resultado financiero final
    fecha_calculo: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """
        Serializa la entidad a diccionarios estándar, útil para 
        pasar los datos hacia puertos de salida (ej. bases de datos, Redis).
        """
        return {
            "evaluacion_id": str(self.evaluacion_id),
            "salario_base_snapshot": float(self.salario_base_snapshot),
            "impacto_ebitda_logrado": float(self.impacto_ebitda_logrado),
            "performance_index": float(self.performance_index),
            "monto_final_bono": float(self.monto_final_bono),
            "fecha_calculo": self.fecha_calculo.isoformat(),
        }