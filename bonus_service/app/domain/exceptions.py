"""
Excepciones de negocio para el bonus_service.
"""


class InvalidCalificacionException(ValueError):
    """Se lanza cuando la calificación global está fuera del rango permitido (1.0-5.0)."""

    def __init__(self, value: float):
        super().__init__(f"Calificación global inválida: {value}. Rango permitido: 1.0 - 5.0.")


class BonusAlreadyCalculatedException(ValueError):
    """Se lanza cuando ya existe un bono calculado para el empleado en el periodo."""

    def __init__(self, empleado_id: int, periodo: str):
        super().__init__(
            f"Ya existe un bono para el empleado {empleado_id} en el periodo '{periodo}'."
        )
