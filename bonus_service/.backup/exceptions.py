"""
Handlers de excepciones para bonus_service.
Cumple: OWASP Error Handling + OWASP SCP - No Information Leakage.

PRINCIPIOS:
- ERRORES 401/403: Nunca revelar si el usuario existe o el token está malformado
- ERROR 422: Detalle genérico de validación
- ERROR 500: Stacktrace NUNCA expuesto al cliente
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidEBITDAException,
    InvalidCalificacionException,
    BonusAlreadyCalculatedException,
)


async def invalid_ebitda_handler(request: Request, exc: InvalidEBITDAException):
    """
    Handler para EBITDA inválido.
    No revela el valor enviado (puede ser dato sensible).
    """
    return JSONResponse(
        status_code=422,
        content={"detail": "Datos de entrada inválidos"},
    )


async def invalid_calificacion_handler(request: Request, exc: InvalidCalificacionException):
    """
    Handler para calificación fuera de rango.
    No revela el valor enviado.
    """
    return JSONResponse(
        status_code=422,
        content={"detail": "Calificación fuera de rango válido"},
    )


async def bonus_already_calculated_handler(request: Request, exc: BonusAlreadyCalculatedException):
    """
    Handler para bono ya calculado.
    Informa que ya existe cálculo (seguro, no revela datos).
    """
    return JSONResponse(
        status_code=409,
        content={"detail": "Ya existe un bono calculado para esta evaluación"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler catch-all que NO revela stack traces ni información de infraestructura.
    
    OWASP Error Handling:
    - No mostrar rutas de archivos
    - No mostrar versiones de librerías
    - No mostrar mensajes de error de BD
    - No mostrar stack traces
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {type(exc).__name__}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
        headers={"Cache-Control": "no-store"},
    )


EXCEPTION_HANDLERS = {
    InvalidEBITDAException: invalid_ebitda_handler,
    InvalidCalificacionException: invalid_calificacion_handler,
    BonusAlreadyCalculatedException: bonus_already_calculated_handler,
    Exception: generic_exception_handler,
}