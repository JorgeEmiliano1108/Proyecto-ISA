class InvalidEBITDAException(Exception):
    """Se lanza cuando el EBITDA logrado es negativo o inválido."""

    def __init__(self, value: float):
        super().__init__(f"EBITDA inválido: {value}. Debe ser un número >= 0.")


class InvalidCalificacionException(Exception):
    """Se lanza cuando la calificación global está fuera del rango permitido (0-5)."""

    def __init__(self, value: float):
        super().__init__(f"Calificación global inválida: {value}. Rango permitido: 0.0 - 5.0.")


class BonusAlreadyCalculatedException(Exception):
    """Se lanza cuando ya existe un bono calculado para el empleado en el periodo."""

    def __init__(self, empleado_id: int, periodo: str):
        super().__init__(
            f"Ya existe un bono para el empleado {empleado_id} en el periodo '{periodo}'."
        )
