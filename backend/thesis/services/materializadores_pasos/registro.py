"""Registro y despacho de reglas relacionales de los pasos."""

from collections.abc import Callable
from dataclasses import dataclass

from thesis.models import Proyecto, PerfilInvestigacion, ProgresoPaso


@dataclass(frozen=True)
class ContextoEjecucionPaso:
    """Contexto inmutable inyectado a cada estrategia de materialización."""

    proyecto: Proyecto
    perfil: PerfilInvestigacion
    codigo_paso: str
    datos_validados: dict


ManejadorPaso = Callable[[ContextoEjecucionPaso], None]
MANEJADORES_PASO: dict[str, ManejadorPaso] = {}


def registrar_manejador_paso(*codigos_paso: str):
    """Decorador del Registro de Estrategias (Strategy Registry) por código de paso."""
    def decorador(funcion: ManejadorPaso) -> ManejadorPaso:
        for codigo in codigos_paso:
            MANEJADORES_PASO[codigo] = funcion
        return funcion
    return decorador


def _obtener_salida_paso_completado(proyecto: Proyecto, codigo_paso: str) -> dict:
    return ProgresoPaso.objects.get(project=proyecto, step_code=codigo_paso).output_json


def ejecutar_materializador_paso(
    proyecto: Proyecto,
    perfil: PerfilInvestigacion,
    codigo_paso: str,
    datos_validados: dict,
) -> None:
    """Despacha la estrategia registrada para `codigo_paso` sin cadenas condicionales."""
    manejador = MANEJADORES_PASO.get(codigo_paso)
    if manejador is not None:
        manejador(ContextoEjecucionPaso(
            proyecto=proyecto,
            perfil=perfil,
            codigo_paso=codigo_paso,
            datos_validados=datos_validados,
        ))
