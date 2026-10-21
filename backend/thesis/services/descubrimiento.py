"""Consulta de catálogos académicos con control de acceso por proyecto."""

from thesis.integrations.semantic_scholar import buscar_articulos
from thesis.services.acceso import requerir_proyecto
from thesis.services.errores import ErrorDominio


def buscar_semantic_scholar_servicio(usuario, id_proyecto, consulta: str, limite: int = 5) -> dict:
    requerir_proyecto(usuario, id_proyecto)
    consulta = consulta.strip()
    if not 3 <= len(consulta) <= 300:
        raise ErrorDominio("ERROR_VALIDACION", "La consulta debe tener entre 3 y 300 caracteres")
    return {
        "proveedor": "SEMANTIC_SCHOLAR",
        "consulta": consulta,
        "resultados": buscar_articulos(consulta, limite),
        "nivel_verificacion": "SOLO_METADATOS",
        "texto_completo_inspeccionado": False,
    }
