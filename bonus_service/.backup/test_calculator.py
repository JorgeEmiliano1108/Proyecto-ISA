"""
Pruebas unitarias críticas para calculator.py.
Sin base de datos, sin red — 100% aisladas.
"""
import pytest
from decimal import Decimal

from app.domain.calculator import calcular_bono_individual, calcular_bonos_batch
from app.domain.exceptions import InvalidEBITDAException, InvalidCalificacionException


# ── calcular_bono_individual ───────────────────────────────────────────────────

class TestCalcularBonoIndividual:
    def test_calculo_correcto_formula(self):
        """
        salario=10_000, ebitda=0.8, calificacion=4.0
        factor_desempeño = 4.0 / 5.0 = 0.80
        multiplicador = (0.80 * 0.60) + (0.80 * 0.40) = 0.48 + 0.32 = 0.80
        monto = 10_000 * 0.80 = 8_000.00
        """
        result = calcular_bono_individual(
            empleado_id=1,
            periodo="2025-Q4",
            salario_base_snapshot=10_000.0,
            impacto_ebitda=0.8,
            calificacion_global=4.0,
        )
        assert result.monto_bono == Decimal("8000.00")
        assert result.empleado_id == 1
        assert result.periodo == "2025-Q4"

    def test_calificacion_maxima(self):
        result = calcular_bono_individual(1, "2025-Q4", 10_000, 1.0, 5.0)
        assert result.monto_bono == Decimal("10000.00")

    def test_calificacion_minima(self):
        result = calcular_bono_individual(1, "2025-Q4", 10_000, 0.0, 0.0)
        assert result.monto_bono == Decimal("0.00")

    def test_ebitda_negativo_lanza_excepcion(self):
        with pytest.raises(InvalidEBITDAException):
            calcular_bono_individual(1, "2025-Q4", 10_000, -0.1, 3.0)

    def test_calificacion_fuera_de_rango_superior(self):
        with pytest.raises(InvalidCalificacionException):
            calcular_bono_individual(1, "2025-Q4", 10_000, 0.5, 5.1)

    def test_calificacion_fuera_de_rango_inferior(self):
        with pytest.raises(InvalidCalificacionException):
            calcular_bono_individual(1, "2025-Q4", 10_000, 0.5, -0.1)

    def test_resultado_es_inmutable(self):
        result = calcular_bono_individual(1, "2025-Q4", 5_000, 0.5, 3.0)
        with pytest.raises(Exception):
            result.monto_bono = Decimal("999.00")  # type: ignore

    def test_redondeo_correcto(self):
        """Verifica que el monto se redondee a 2 decimales correctamente."""
        result = calcular_bono_individual(1, "2025-Q4", 1_000, 0.333, 2.5)
        assert result.monto_bono == result.monto_bono.quantize(Decimal("0.01"))


# ── calcular_bonos_batch ───────────────────────────────────────────────────────

class TestCalcularBonosBatch:
    def _make_registro(self, empleado_id: int, calificacion: float = 4.0) -> dict:
        return {
            "empleado_id": empleado_id,
            "periodo": "2025-Q4",
            "salario_base_snapshot": 10_000.0,
            "impacto_ebitda": 0.8,
            "calificacion_global": calificacion,
        }

    def test_batch_vacio_devuelve_lista_vacia(self):
        assert calcular_bonos_batch([]) == []

    def test_batch_multiples_empleados(self):
        registros = [self._make_registro(i) for i in range(1, 6)]
        resultados = calcular_bonos_batch(registros)
        assert len(resultados) == 5
        for r in resultados:
            assert r.monto_bono > Decimal("0")

    def test_batch_ebitda_invalido_lanza_excepcion(self):
        registros = [self._make_registro(1)]
        registros[0]["impacto_ebitda"] = -0.5
        with pytest.raises(InvalidEBITDAException):
            calcular_bonos_batch(registros)

    def test_batch_calificacion_invalida_lanza_excepcion(self):
        registros = [self._make_registro(1, calificacion=6.0)]
        with pytest.raises(InvalidCalificacionException):
            calcular_bonos_batch(registros)

    def test_batch_consistente_con_individual(self):
        """El resultado batch debe ser idéntico al individual para el mismo input."""
        registro = self._make_registro(42, calificacion=3.5)
        batch_result = calcular_bonos_batch([registro])[0]
        individual_result = calcular_bono_individual(**{
            k: registro[k] for k in
            ["empleado_id", "periodo", "salario_base_snapshot", "impacto_ebitda", "calificacion_global"]
        })
        assert batch_result.monto_bono == individual_result.monto_bono
