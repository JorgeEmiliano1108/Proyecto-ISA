"""
Núcleo matemático del bonus_service.
Cero dependencias web. 100% testeable de forma aislada.

NUEVA REGLA DE NEGOCIO:
──────────────────────────────────────────────────────────────────────────────
  porcentaje_logro = calificacion_global * 20.0
  (1.0 = 20%, 2.0 = 40%, ..., 5.0 = 100%)
──────────────────────────────────────────────────────────────────────────────
"""
import uuid
from typing import List

import numpy as np
import pandas as pd

from app.domain.entities import CalculoLogro
from app.domain.exceptions import InvalidCalificacionException


def _validate_calificacion(calificacion_global: float) -> None:
    """Valida que la calificación global esté estrictamente entre 1.0 y 5.0."""
    if not (1.0 <= calificacion_global <= 5.0):
        raise InvalidCalificacionException(calificacion_global)


def calcular_logro_individual(
    evaluacion_id: uuid.UUID,
    calificacion_global: float,
) -> CalculoLogro:
    """Calcula el porcentaje de logro para una evaluación."""
    _validate_calificacion(calificacion_global)

    porcentaje_logro = round(calificacion_global * 20.0, 2)

    return CalculoLogro(
        evaluacion_id=evaluacion_id,
        calificacion_global=calificacion_global,
        porcentaje_logro=porcentaje_logro,
    )


def calcular_logros_batch(registros: List[dict]) -> List[CalculoLogro]:
    """
    Cálculo vectorizado para múltiples evaluaciones.
    Cada registro debe contener: evaluacion_id, calificacion_global
    
    Optimización: Usa zip() en lugar de iterrows() para mejor performance.
    """
    if not registros:
        return []

    df = pd.DataFrame(registros)

    # Validación vectorizada de calificaciones
    cal_invalida = df[(df["calificacion_global"] < 1.0) | (df["calificacion_global"] > 5.0)]
    if not cal_invalida.empty:
        raise InvalidCalificacionException(float(cal_invalida["calificacion_global"].iloc[0]))

    # Cálculo vectorizado con NumPy
    evaluacion_ids = df["evaluacion_id"].to_numpy()
    calificaciones = df["calificacion_global"].to_numpy(dtype=np.float64)
    porcentajes = np.round(calificaciones * 20.0, decimals=2)

    # Construcción eficiente usando zip() en lugar de iterrows()
    resultados: List[CalculoLogro] = [
        CalculoLogro(
            evaluacion_id=uuid.UUID(str(eid)),
            calificacion_global=float(cal),
            porcentaje_logro=float(por),
        )
        for eid, cal, por in zip(evaluacion_ids, calificaciones, porcentajes)
    ]

    return resultados
