"""Servicio de búsqueda y clasificación de antecedentes científicos nacionales y locales (Perú)."""

from typing import Any

from thesis.integrations.alicia import buscar_tesis_alicia
from thesis.integrations.peru_articles import buscar_articulos_afiliacion_peru
from thesis.models import PerfilInvestigacion
from thesis.services.access import requerir_proyecto
from thesis.services.errors import ErrorDominio
from thesis.services.geography import AlcanceGeografico, _contiene_termino, _quitar_tildes, resolver_alcance_geografico


def _clasificar_localidad(item: dict, scope: AlcanceGeografico) -> tuple[bool, str]:
    """Evalúa de forma determinista si un registro califica como local y explica la razón."""
    title_clean = _quitar_tildes(item.get("title") or "")
    abstract_clean = _quitar_tildes(item.get("abstract") or "")
    combined_text = f"{title_clean} {abstract_clean}"

    # 1. Comprobar si la institución es una universidad local de la zona (por acrónimo o nombre de región)
    inst_clean = _quitar_tildes(item.get("institution") or "")
    region_clean = _quitar_tildes(scope.region)
    if scope.match_keywords and _contiene_termino(inst_clean, region_clean):
        return True, f"LOCAL_POR_INSTITUCION: {item.get('institution')}"

    for local_inst in scope.local_institutions:
        if _contiene_termino(inst_clean, local_inst):
            return True, f"LOCAL_POR_INSTITUCION: {item.get('institution')}"

    # 2. Comprobar si el objeto de estudio, población o empresa está en la localidad
    for kw in scope.match_keywords:
        if _contiene_termino(combined_text, kw) or _contiene_termino(inst_clean, kw):
            return True, f"LOCAL_POR_OBJETO_ESTUDIO: Coincidencia geográfica con '{kw}'"

    return False, "NACIONAL: Ámbito general Perú"


def buscar_antecedentes_peru_servicio(
    actor,
    project_id,
    query: str,
    scope_filter: str = "todos",
    include_articles: bool = True,
    limit: int = 5,
) -> dict[str, Any]:
    """Busca tesis en ALICIA y artículos con filiación peruana, sin certificar arbitraje."""
    project = requerir_proyecto(actor, project_id)
    query = query.strip()
    if not query:
        raise ErrorDominio("VALIDATION_ERROR", "La consulta de búsqueda no puede estar vacía")
    if scope_filter not in ("todos", "locales", "nacionales"):
        raise ErrorDominio("VALIDATION_ERROR", "scope_filter debe ser 'todos', 'locales' o 'nacionales'")
    if not 1 <= limit <= 20:
        raise ErrorDominio("VALIDATION_ERROR", "limit debe estar entre 1 y 20")

    profile = PerfilInvestigacion.objects.filter(project=project).first()
    place = profile.place if profile else None
    scope = resolver_alcance_geografico(place)
    if scope_filter == "locales" and not scope.match_keywords:
        raise ErrorDominio("VALIDATION_ERROR", "Configura el lugar del proyecto antes de buscar antecedentes locales")

    raw_candidates: list[dict] = []
    provider_errors: list[str] = []
    provider_successes = 0

    # 1. Búsqueda local orientada a la región
    if scope_filter in ("todos", "locales") and scope.match_keywords:
        try:
            local_query = f"{query} {scope.region}"
            theses_local = buscar_tesis_alicia(local_query, limit=limit)
            raw_candidates.extend(theses_local)
            provider_successes += 1
        except ErrorDominio:
            provider_errors.append("ALICIA_LOCAL")

    # 2. Búsqueda nacional en ALICIA
    if scope_filter in ("todos", "nacionales") or len(raw_candidates) < limit:
        try:
            theses_national = buscar_tesis_alicia(query, limit=limit)
            raw_candidates.extend(theses_national)
            provider_successes += 1
        except ErrorDominio:
            provider_errors.append("ALICIA_NACIONAL")

    # 3. Artículos con filiación peruana; la revisión por pares queda sin acreditar.
    if include_articles:
        try:
            articles = buscar_articulos_afiliacion_peru(query, limit=min(limit, 5))
            raw_candidates.extend(articles)
            provider_successes += 1
        except ErrorDominio:
            provider_errors.append("OPENALEX_PERU")
    if not provider_successes:
        raise ErrorDominio("SEARCH_UNAVAILABLE", "No se pudo consultar ningún proveedor de antecedentes peruanos")

    # Clasificación y deduplicación por título normalizado
    seen_titles = set()
    classified_results = []
    for item in raw_candidates:
        title_key = (item.get("title") or "").strip().lower()
        if not title_key or title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        is_local, justification = _clasificar_localidad(item, scope)
        item["es_local"] = is_local
        item["justificacion_local"] = justification
        item["region_evaluada"] = scope.region

        # Filtrar según la opción seleccionada
        if scope_filter == "locales" and not is_local:
            continue
        if scope_filter == "nacionales" and is_local:
            continue

        classified_results.append(item)

    # Ordenar: si es "todos", priorizar los locales primero, luego por año descendente
    def _clave_ordenamiento(doc: dict):
        local_weight = 0 if doc.get("es_local") else 1
        year_weight = -(doc.get("publication_year") or 0)
        return (local_weight, year_weight)

    classified_results.sort(key=_clave_ordenamiento)
    final_list = classified_results[:limit]

    return {
        "project_id": str(project.id),
        "query": query,
        "region_detectada": scope.region,
        "scope_filter": scope_filter,
        "total_encontrados": len(final_list),
        "resultados": final_list,
        "fuentes_no_disponibles": provider_errors,
        "verification_level": "METADATA_ONLY",
        "full_text_inspected": False,
    }
