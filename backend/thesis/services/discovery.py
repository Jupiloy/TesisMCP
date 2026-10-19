"""Consulta de catálogos académicos con control de acceso por proyecto."""

from thesis.integrations.semantic_scholar import buscar_articulos
from thesis.services.access import requerir_proyecto
from thesis.services.errors import ErrorDominio


def buscar_semantic_scholar_servicio(actor, project_id, query: str, limit: int = 5) -> dict:
    requerir_proyecto(actor, project_id)
    query = query.strip()
    if not 3 <= len(query) <= 300:
        raise ErrorDominio("VALIDATION_ERROR", "La consulta debe tener entre 3 y 300 caracteres")
    return {
        "provider": "SEMANTIC_SCHOLAR",
        "query": query,
        "results": buscar_articulos(query, limit),
        "verification_level": "METADATA_ONLY",
        "full_text_inspected": False,
    }
