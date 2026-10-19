"""Adaptador para la API REST de ALICIA (CONCYTEC).

Devuelve exclusivamente metadatos normalizados (METADATA_ONLY); no afirma inspección de texto completo.
"""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errors import ErrorDominio

ALICIA_API_URL = "https://alicia.concytec.gob.pe/vufind/api/v1/search"


def _solicitar_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ErrorDominio("SEARCH_UNAVAILABLE", "No se pudo consultar el catálogo de ALICIA CONCYTEC") from exc
    if not isinstance(payload, dict):
        raise ErrorDominio("SEARCH_UNAVAILABLE", "ALICIA CONCYTEC devolvió una respuesta inesperada")
    return payload


def _extraer_autores(raw_authors: dict | list | None) -> list[str]:
    if not isinstance(raw_authors, dict):
        return []
    names = []
    primary = raw_authors.get("primary") or {}
    if isinstance(primary, dict):
        names.extend(list(primary.keys()))
    # Los nombres secundarios pueden corresponder a asesores o colaboradores.
    return [name.strip() for name in names if name and name.strip()]


def _extraer_identificador_handle(urls: list[dict] | None) -> str | None:
    if not isinstance(urls, list):
        return None
    for entry in urls:
        if isinstance(entry, dict) and entry.get("url"):
            u = entry["url"]
            if "hdl.handle.net" in u or "handle" in u or "repositorio" in u:
                return u
    return urls[0].get("url") if urls and isinstance(urls[0], dict) else None


def _normalizar_registro_alicia(registrar_resultado: dict) -> dict | None:
    if not isinstance(registrar_resultado, dict) or not registrar_resultado.get("title"):
        return None

    urls = registrar_resultado.get("urls") or []
    handle = _extraer_identificador_handle(urls)
    authors = _extraer_autores(registrar_resultado.get("authors"))

    # Intentar obtener el año de publicación
    year = None
    pub_dates = registrar_resultado.get("publicationDates") or registrar_resultado.get("dcDateIssued") or []
    first_date = pub_dates[0] if isinstance(pub_dates, list) and pub_dates else pub_dates
    match = re.search(r"\b(?:19|20)\d{2}\b", str(first_date)) if first_date else None
    if match:
        year = int(match.group())

    grantor = registrar_resultado.get("thesisDegreeGrantor")
    if isinstance(grantor, list) and grantor:
        institution = str(grantor[0])
    else:
        publisher = registrar_resultado.get("institution") or registrar_resultado.get("dcPublisher")
        institution = str(publisher[0] if isinstance(publisher, list) and publisher else publisher) if publisher else None

    abstract_list = registrar_resultado.get("dcDescriptionAbstract") or []
    abstract = abstract_list[0] if isinstance(abstract_list, list) and abstract_list else (
        abstract_list if isinstance(abstract_list, str) else ""
    )

    return {
        "source_origin": "ALICIA_CONCYTEC",
        "record_id": registrar_resultado.get("id"),
        "title": registrar_resultado["title"].strip(),
        "authors": authors,
        "publication_year": year,
        "institution": institution,
        "handle_url": handle,
        "landing_page_url": handle,
        "abstract": abstract,
        "verification_level": "METADATA_ONLY",
        "full_text_inspected": False,
    }


def buscar_tesis_alicia(query: str, institutions: list[str] | None = None, limit: int = 5) -> list[dict]:
    """Busca tesis en ALICIA (CONCYTEC) aplicando opcionalmente filtros institucionales."""
    if not 1 <= limit <= 20:
        raise ErrorDominio("VALIDATION_ERROR", "limit debe estar entre 1 y 20")

    query = query.strip()
    if not query:
        raise ErrorDominio("VALIDATION_ERROR", "La consulta de búsqueda no puede estar vacía")

    params = [("lookfor", query), ("limit", str(limit))]
    if institutions:
        for inst in institutions:
            params.append(("filter[]", f'institution:"{inst}"'))

    url = f"{ALICIA_API_URL}?{urlencode(params)}"
    payload = _solicitar_json(url)

    results = []
    for raw in payload.get("records") or []:
        norm = _normalizar_registro_alicia(raw)
        if norm:
            results.append(norm)
    return results
