"""
Núcleo Matemático del bonus_service.
Cero dependencias web. 100% testeable de forma aislada.

Campos reales de la tabla 'bonos':
  - salario_base_snapshot   → DECIMAL(12,2)
  - impacto_ebitda_logrado  → DECIMAL(5,2)   % logrado del EBITDA corporativo
  - performance_index       → DECIMAL(5,2)   derivado de calificacion_global
  - monto_final_bono        → DECIMAL(12,2)

Fórmula financiera corporativa ISA:
──────────────────────────────────────────────────────────────────────────────
  performance_index  = calificacion_global / 5.0          (0.0 – 1.0)
  factor_ebitda      = impacto_ebitda_logrado / 100.0     (normalizado a 0-1)
  multiplicador      = (performance_index * 0.60) + (factor_ebitda * 0.40)
  monto_final_bono   = salario_base_snapshot * multiplicador
──────────────────────────────────────────────────────────────────────────────
"""

import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import List

import numpy as np
import pandas as pd

from app.domain.entities import BonusCalculation
from app.domain.exceptions import InvalidEBITDAException, InvalidCalificacionException

PESO_DESEMPENIO: float = 0.60
PESO_CORPORATIVO: float = 0.40


def _validate_inputs(impacto_ebitda_logrado: float, calificacion_global: float) -> None:
    if impacto_ebitda_logrado < 0:
        raise InvalidEBITDAException(impacto_ebitda_logrado)
    if not (1.0 <= calificacion_global <= 5.0):
        raise InvalidCalificacionException(calificacion_global)


def calcular_bono_individual(
    evaluacion_id: uuid.UUID,
    salario_base_snapshot: float,
    impacto_ebitda_logrado: float,   # Valor en % ej: 85.50
    calificacion_global: float,       # 1.0 – 5.0
) -> BonusCalculation:
    """Calcula el bono para una evaluación. Devuelve una entidad inmutable."""
    _validate_inputs(impacto_ebitda_logrado, calificacion_global)

    performance_index = calificacion_global / 5.0
    factor_ebitda = impacto_ebitda_logrado / 100.0
    multiplicador = (performance_index * PESO_DESEMPENIO) + (factor_ebitda * PESO_CORPORATIVO)
    monto_raw = salario_base_snapshot * multiplicador

    monto_final = Decimal(str(monto_raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    perf_idx_decimal = Decimal(str(round(performance_index, 2)))

    return BonusCalculation(
        evaluacion_id=evaluacion_id,
        salario_base_snapshot=Decimal(str(salario_base_snapshot)),
        impacto_ebitda_logrado=Decimal(str(impacto_ebitda_logrado)),
        performance_index=perf_idx_decimal,
        monto_final_bono=monto_final,
    )


def calcular_bonos_batch(registros: List[dict]) -> List[BonusCalculation]:
    """
    Cálculo vectorizado para múltiples evaluaciones (Celery batch).
    Cada registro debe contener:
        evaluacion_id, salario_base_snapshot, impacto_ebitda_logrado, calificacion_global
    """
    if not registros:
        return []

    df = pd.DataFrame(registros)

    ebitda_invalido = df[df["impacto_ebitda_logrado"] < 0]
    if not ebitda_invalido.empty:
        raise InvalidEBITDAException(float(ebitda_invalido["impacto_ebitda_logrado"].iloc[0]))

    cal_invalida = df[(df["calificacion_global"] < 1) | (df["calificacion_global"] > 5)]
    if not cal_invalida.empty:
        raise InvalidCalificacionException(float(cal_invalida["calificacion_global"].iloc[0]))

    salarios = df["salario_base_snapshot"].to_numpy(dtype=np.float64)
    ebitda = df["impacto_ebitda_logrado"].to_numpy(dtype=np.float64) / 100.0
    calificaciones = df["calificacion_global"].to_numpy(dtype=np.float64)

    performance_indexes = calificaciones / 5.0
    multiplicadores = (performance_indexes * PESO_DESEMPENIO) + (ebitda * PESO_CORPORATIVO)
    montos = np.round(salarios * multiplicadores, decimals=2)

    resultados: List[BonusCalculation] = []
    for i, row in df.iterrows():
        resultados.append(
            BonusCalculation(
                evaluacion_id=uuid.UUID(str(row["evaluacion_id"])),
                salario_base_snapshot=Decimal(str(row["salario_base_snapshot"])),
                impacto_ebitda_logrado=Decimal(str(row["impacto_ebitda_logrado"])),
                performance_index=Decimal(str(round(performance_indexes[i], 2))),
                monto_final_bono=Decimal(str(montos[i])),
            )
        )

    return resultados
