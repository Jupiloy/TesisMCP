"""Búsqueda de metadatos en Semantic Scholar Academic Graph."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errors import ErrorDominio


SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,year,authors,url,externalIds,openAccessPdf"


def buscar_articulos(query: str, limit: int = 5) -> list[dict]:
    if not 1 <= limit <= 10:
        raise ErrorDominio("VALIDATION_ERROR", "limit debe estar entre 1 y 10")
    params = urlencode({"query": query, "limit": limit, "fields": FIELDS})
    headers = {"User-Agent": "TesisMCP/0.1 (academic discovery)", "Accept": "application/json"}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if api_key:
        headers["x-api-key"] = api_key
    request = Request(f"{SEARCH_URL}?{params}", headers=headers)
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ErrorDominio("SEARCH_UNAVAILABLE", "No se pudo consultar Semantic Scholar") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ErrorDominio("SEARCH_UNAVAILABLE", "Semantic Scholar devolvió una respuesta inesperada")
    papers = []
    for paper in payload["data"]:
        if not isinstance(paper, dict) or not paper.get("paperId") or not paper.get("title"):
            continue
        external_ids = paper.get("externalIds") or {}
        access = paper.get("openAccessPdf") or {}
        papers.append({
            "provider": "SEMANTIC_SCHOLAR",
            "record_id": paper["paperId"],
            "title": paper["title"],
            "authors": [a["name"] for a in (paper.get("authors") or []) if isinstance(a, dict) and a.get("name")],
            "publication_year": paper.get("year"),
            "doi": external_ids.get("DOI") if isinstance(external_ids, dict) else None,
            "record_url": paper.get("url"),
            "pdf_url_candidate": access.get("url") if isinstance(access, dict) else None,
            "verification_level": "METADATA_ONLY",
            "full_text_inspected": False,
        })
    return papers
