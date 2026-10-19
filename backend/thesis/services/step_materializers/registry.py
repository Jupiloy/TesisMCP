"""Registro y despacho de reglas relacionales de los pasos."""

from collections.abc import Callable
from dataclasses import dataclass

from thesis.models import Proyecto, PerfilInvestigacion, ProgresoPaso


@dataclass(frozen=True)
class ContextoEjecucionPaso:
    """Contexto inmutable inyectado a cada estrategia de materialización."""

    project: Proyecto
    profile: PerfilInvestigacion
    step_code: str
    validated: dict


StepHandler = Callable[[ContextoEjecucionPaso], None]
MANEJADORES_PASO: dict[str, StepHandler] = {}


def registrar_manejador_paso(*step_codes: str):
    """Decorador del Registro de Estrategias (Strategy Registry) por código de paso."""
    def decorador(func: StepHandler) -> StepHandler:
        for code in step_codes:
            MANEJADORES_PASO[code] = func
        return func
    return decorador


def _obtener_salida_paso_completado(project: Proyecto, step_code: str) -> dict:
    return ProgresoPaso.objects.get(project=project, step_code=step_code).output_json


def ejecutar_materializador_paso(project: Proyecto, profile: PerfilInvestigacion, step_code: str, validated: dict) -> None:
    """Despacha la estrategia registrada para `step_code` sin cadenas `if/elif`."""
    manejador = MANEJADORES_PASO.get(step_code)
    if manejador is not None:
        manejador(ContextoEjecucionPaso(project=project, profile=profile, step_code=step_code, validated=validated))
