"""Adaptador para buscar artículos con al menos una filiación institucional peruana.

La clasificación de OpenAlex y el país de filiación no acreditan revisión por pares.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errors import ErrorDominio

OPENALEX_PERU_URL = "https://api.openalex.org/works"


def buscar_articulos_afiliacion_peru(query: str, limit: int = 5) -> list[dict]:
    """Busca trabajos de tipo artículo con filiación en instituciones peruanas."""
    if not 1 <= limit <= 10:
        raise ErrorDominio("VALIDATION_ERROR", "limit debe estar entre 1 y 10")

    query = query.strip()
    if not query:
        raise ErrorDominio("VALIDATION_ERROR", "La consulta de búsqueda no puede estar vacía")

    params = {
        "search": query,
        "filter": "authorships.institutions.country_code:PE",
        "per_page": limit,
    }
    url = f"{OPENALEX_PERU_URL}?{urlencode(params)}"
    request = Request(
        url,
        headers={"User-Agent": "TesisMCP/0.1 (academic discovery with Peruvian affiliation)", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ErrorDominio("SEARCH_UNAVAILABLE", "No se pudo consultar el catálogo de artículos peruanos") from exc

    results = []
    for work in payload.get("results") or []:
        if not isinstance(work, dict) or not work.get("title") or work.get("type") != "article":
            continue

        authors = []
        institutions = []
        for authorship in work.get("authorships") or []:
            if isinstance(authorship, dict):
                author = authorship.get("author") or {}
                if isinstance(author, dict) and author.get("display_name"):
                    authors.append(author["display_name"])
                for inst in authorship.get("institutions") or []:
                    if isinstance(inst, dict) and inst.get("display_name"):
                        institutions.append(inst["display_name"])

        location = work.get("best_oa_location") or {}
        landing_page = location.get("landing_page_url") or (work.get("primary_location") or {}).get("landing_page_url") or work.get("id")

        results.append({
            "source_origin": "ARTICULO_CON_FILIACION_PERUANA",
            "record_id": work.get("id"),
            "title": work["title"].strip(),
            "authors": authors,
            "publication_year": work.get("publication_year"),
            "doi": work.get("doi"),
            "institutions": list(set(institutions)),
            "landing_page_url": landing_page,
            "pdf_url": location.get("pdf_url"),
            "peer_review_verified": False,
            "verification_level": "METADATA_ONLY",
            "full_text_inspected": False,
        })
    return results
