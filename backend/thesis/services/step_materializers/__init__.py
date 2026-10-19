"""Materializadores de pasos metodológicos para los Capítulos 1 al 3 (P01-P12)."""

from . import consistency  # noqa: F401
from .registry import (
    MANEJADORES_PASO,
    ContextoEjecucionPaso,
    ejecutar_materializador_paso,
    registrar_manejador_paso,
)

__all__ = [
    "ContextoEjecucionPaso",
    "MANEJADORES_PASO",
    "ejecutar_materializador_paso",
    "registrar_manejador_paso",
]
