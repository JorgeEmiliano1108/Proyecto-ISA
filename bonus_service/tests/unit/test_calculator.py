"""
Pruebas unitarias críticas para calculator.py.
Sin base de datos, sin red — 100% aisladas.

CUBIERTA:
- Valores límite (1.0, 5.0)
- Valores fuera de rango (0.0, 6.0, negativos)
- Valores decimales
- Batch processing
- Inmutabilidad de entidades
"""
import pytest
import uuid

from app.domain.calculator import calcular_logro_individual, calcular_logros_batch
from app.domain.exceptions import InvalidCalificacionException


class TestCalcularLogroIndividual:
    """Tests para cálculo individual de logro."""

    def test_calculo_correcto_4_0(self):
        """calificacion=4.0 → porcentaje=80.0"""
        eval_id = uuid.uuid4()
        result = calcular_logro_individual(
            evaluacion_id=eval_id,
            calificacion_global=4.0,
        )
        assert result.evaluacion_id == eval_id
        assert result.calificacion_global == 4.0
        assert result.porcentaje_logro == 80.0

    def test_calculo_correcto_1_0_limite_inferior(self):
        """calificacion=1.0 (límite inferior) → porcentaje=20.0"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=1.0,
        )
        assert result.porcentaje_logro == 20.0

    def test_calculo_correcto_5_0_limite_superior(self):
        """calificacion=5.0 (límite superior) → porcentaje=100.0"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=5.0,
        )
        assert result.porcentaje_logro == 100.0

    def test_calculo_correcto_3_0_medio(self):
        """calificacion=3.0 → porcentaje=60.0"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=3.0,
        )
        assert result.porcentaje_logro == 60.0

    def test_calculo_correcto_2_5_decimal(self):
        """calificacion=2.5 → porcentaje=50.0"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=2.5,
        )
        assert result.porcentaje_logro == 50.0

    def test_calculo_correcto_4_75_decimal(self):
        """calificacion=4.75 → porcentaje=95.0"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=4.75,
        )
        assert result.porcentaje_logro == 95.0

    def test_calificacion_0_0_lanza_excepcion(self):
        """calificacion=0.0 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException) as exc_info:
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=0.0,
            )
        assert "0.0" in str(exc_info.value)

    def test_calificacion_0_5_lanza_excepcion(self):
        """calificacion=0.5 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException):
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=0.5,
            )

    def test_calificacion_5_5_lanza_excepcion(self):
        """calificacion=5.5 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException):
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=5.5,
            )

    def test_calificacion_6_0_lanza_excepcion(self):
        """calificacion=6.0 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException):
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=6.0,
            )

    def test_calificacion_negativa_lanza_excepcion(self):
        """calificacion=-1.0 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException):
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=-1.0,
            )

    def test_calificacion_muy_alta_lanza_excepcion(self):
        """calificacion=100.0 debe lanzar InvalidCalificacionException"""
        with pytest.raises(InvalidCalificacionException):
            calcular_logro_individual(
                evaluacion_id=uuid.uuid4(),
                calificacion_global=100.0,
            )

    def test_resultado_es_inmutable(self):
        """La entidad CalculoLogro debe ser inmutable (frozen dataclass)"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=3.0,
        )
        with pytest.raises(Exception):
            result.porcentaje_logro = 99.0

    def test_fecha_calculo_se_establece(self):
        """La fecha_calculo debe establecerse automáticamente"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=3.0,
        )
        assert result.fecha_calculo is not None

    def test_serializacion_a_dict(self):
        """to_dict() debe serializar correctamente"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=4.0,
        )
        data = result.to_dict()
        assert "evaluacion_id" in data
        assert "calificacion_global" in data
        assert "porcentaje_logro" in data
        assert "fecha_calculo" in data
        assert data["porcentaje_logro"] == 80.0


class TestCalcularLogrosBatch:
    """Tests para cálculo batch de logros."""

    def test_batch_vacio_devuelve_lista_vacia(self):
        """Batch vacío debe retornar []"""
        assert calcular_logros_batch([]) == []

    def test_batch_un_solo_registro(self):
        """Batch con un registro debe funcionar correctamente"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 4.0}
        ]
        resultados = calcular_logros_batch(registros)
        assert len(resultados) == 1
        assert resultados[0].porcentaje_logro == 80.0

    def test_batch_multiples_calificaciones_completas(self):
        """Batch con todas las calificaciones válidas"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": float(i)}
            for i in range(1, 6)
        ]
        resultados = calcular_logros_batch(registros)
        assert len(resultados) == 5
        assert resultados[0].porcentaje_logro == 20.0   # 1.0 * 20
        assert resultados[1].porcentaje_logro == 40.0   # 2.0 * 20
        assert resultados[2].porcentaje_logro == 60.0   # 3.0 * 20
        assert resultados[3].porcentaje_logro == 80.0   # 4.0 * 20
        assert resultados[4].porcentaje_logro == 100.0  # 5.0 * 20

    def test_batch_calificacion_invalida_baja_lanza_excepcion(self):
        """Batch con calificación < 1.0 debe lanzar excepción"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 0.0}
        ]
        with pytest.raises(InvalidCalificacionException):
            calcular_logros_batch(registros)

    def test_batch_calificacion_invalida_alta_lanza_excepcion(self):
        """Batch con calificación > 5.0 debe lanzar excepción"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 6.0}
        ]
        with pytest.raises(InvalidCalificacionException):
            calcular_logros_batch(registros)

    def test_batch_primero_invalido_lanza_excepcion(self):
        """Batch donde el primer registro es inválido debe lanzar excepción"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 0.5},
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 4.0},
        ]
        with pytest.raises(InvalidCalificacionException):
            calcular_logros_batch(registros)

    def test_batch_ultimo_invalido_lanza_excepcion(self):
        """Batch donde el último registro es inválido debe lanzar excepción"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 4.0},
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 5.5},
        ]
        with pytest.raises(InvalidCalificacionException):
            calcular_logros_batch(registros)

    def test_batch_consistente_con_individual(self):
        """El resultado batch debe ser idéntico al individual para el mismo input."""
        eval_id = str(uuid.uuid4())
        registro = {"evaluacion_id": eval_id, "calificacion_global": 3.5}
        batch_result = calcular_logros_batch([registro])[0]
        individual_result = calcular_logro_individual(
            evaluacion_id=uuid.UUID(eval_id),
            calificacion_global=3.5,
        )
        assert batch_result.porcentaje_logro == individual_result.porcentaje_logro
        assert batch_result.calificacion_global == individual_result.calificacion_global

    def test_batch_decimales_precisos(self):
        """Batch con decimales debe mantener precisión"""
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 1.25},
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 2.75},
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 3.33},
        ]
        resultados = calcular_logros_batch(registros)
        assert len(resultados) == 3
        assert resultados[0].porcentaje_logro == 25.0    # 1.25 * 20
        assert resultados[1].porcentaje_logro == 55.0    # 2.75 * 20
        assert resultados[2].porcentaje_logro == 66.6    # 3.33 * 20

    def test_batch_uuids_preservados(self):
        """Batch debe preservar los UUIDs originales"""
        eval_id_1 = uuid.uuid4()
        eval_id_2 = uuid.uuid4()
        registros = [
            {"evaluacion_id": str(eval_id_1), "calificacion_global": 3.0},
            {"evaluacion_id": str(eval_id_2), "calificacion_global": 4.0},
        ]
        resultados = calcular_logros_batch(registros)
        assert resultados[0].evaluacion_id == eval_id_1
        assert resultados[1].evaluacion_id == eval_id_2

    def test_batch_grande_performance(self):
        """Batch grande debe procesarse correctamente (test de performance básico)"""
        import time
        n_registros = 1000
        registros = [
            {"evaluacion_id": str(uuid.uuid4()), "calificacion_global": 3.0}
            for _ in range(n_registros)
        ]
        
        start = time.time()
        resultados = calcular_logros_batch(registros)
        elapsed = time.time() - start
        
        assert len(resultados) == n_registros
        assert elapsed < 5.0  # Debe completarse en menos de 5 segundos


class TestFórmulaMatemática:
    """Tests específicos para validar la fórmula matemática."""

    @pytest.mark.parametrize(
        "calificacion,porcentaje_esperado",
        [
            (1.0, 20.0),
            (1.5, 30.0),
            (2.0, 40.0),
            (2.5, 50.0),
            (3.0, 60.0),
            (3.5, 70.0),
            (4.0, 80.0),
            (4.5, 90.0),
            (5.0, 100.0),
        ]
    )
    def test_formula_calificacion_a_porcentaje(self, calificacion, porcentaje_esperado):
        """Valida que la fórmula calificacion * 20 sea correcta"""
        result = calcular_logro_individual(
            evaluacion_id=uuid.uuid4(),
            calificacion_global=calificacion,
        )
        assert result.porcentaje_logro == porcentaje_esperado

    def test_formula_linealidad(self):
        """Valida que la relación sea lineal (doble calificación = doble porcentaje)"""
        r1 = calcular_logro_individual(uuid.uuid4(), 2.0)
        r2 = calcular_logro_individual(uuid.uuid4(), 4.0)
        assert r2.porcentaje_logro == r1.porcentaje_logro * 2