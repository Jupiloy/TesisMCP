"""Adaptador HTTP: nunca convierte metadatos en evidencia de texto completo."""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errors import ErrorDominio


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
WORK_ID = re.compile(r"^(?:https://openalex\.org/)?(W[1-9][0-9]*)$")


def _solicitar_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "TesisMCP/0.1 (academic discovery)", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ErrorDominio("SEARCH_UNAVAILABLE", "No se pudo consultar el registro en OpenAlex") from exc
    if not isinstance(payload, dict):
        raise ErrorDominio("SEARCH_UNAVAILABLE", "OpenAlex devolvió una respuesta inesperada")
    return payload


def obtener_trabajo_openalex(openalex_id: str) -> dict:
    match = WORK_ID.fullmatch(openalex_id.strip())
    if not match:
        raise ErrorDominio("VALIDATION_ERROR", "Identificador OpenAlex inválido")
    work_id = match.group(1)
    params = {}
    email = os.getenv("OPENALEX_CONTACT_EMAIL", "").strip()
    if email:
        params["mailto"] = email
    suffix = f"?{urlencode(params)}" if params else ""
    work = _solicitar_json(f"{OPENALEX_WORKS_URL}/{work_id}{suffix}")
    normalized = _normalizar_trabajo(work)
    if normalized is None or normalized["openalex_id"] != f"https://openalex.org/{work_id}":
        raise ErrorDominio("SEARCH_UNAVAILABLE", "OpenAlex no devolvió el trabajo solicitado")
    return normalized


def buscar_trabajos_openalex(query: str, limit: int = 5) -> list[dict]:
    if not 1 <= limit <= 10:
        raise ErrorDominio("VALIDATION_ERROR", "limit debe estar entre 1 y 10")
    params = {"search": query, "per_page": limit}
    email = os.getenv("OPENALEX_CONTACT_EMAIL", "").strip()
    if email:
        params["mailto"] = email
    payload = _solicitar_json(f"{OPENALEX_WORKS_URL}?{urlencode(params)}")

    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ErrorDominio("SEARCH_UNAVAILABLE", "OpenAlex devolvió una respuesta inesperada")

    works = []
    for work in payload["results"]:
        normalized = _normalizar_trabajo(work)
        if normalized:
            works.append(normalized)
    return works


def _normalizar_trabajo(work: dict) -> dict | None:
    if not isinstance(work, dict) or not work.get("id") or not work.get("title"):
        return None
    authors = []
    for authorship in work.get("authorships") or []:
        if isinstance(authorship, dict):
            author = authorship.get("author") or {}
            if isinstance(author, dict) and author.get("display_name"):
                authors.append(author["display_name"])
    location = work.get("best_oa_location") or {}
    primary = work.get("primary_location") or {}
    if not isinstance(location, dict):
        location = {}
    if not isinstance(primary, dict):
        primary = {}
    return {
        "openalex_id": work["id"], "title": work["title"], "authors": authors,
        "publication_year": work.get("publication_year"), "doi": work.get("doi"),
        "record_url": work["id"],
        "landing_page_url": location.get("landing_page_url") or primary.get("landing_page_url"),
        "pdf_url": location.get("pdf_url"), "openalex_retracted": work.get("is_retracted"),
        "verification_level": "METADATA_ONLY",
        "full_text_inspected": False,
    }
