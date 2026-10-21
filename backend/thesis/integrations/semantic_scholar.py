"""Búsqueda de metadatos en Semantic Scholar Academic Graph."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errores import ErrorDominio


URL_BUSQUEDA = "https://api.semanticscholar.org/graph/v1/paper/search"
CAMPOS = "title,year,authors,url,externalIds,openAccessPdf"


def buscar_articulos(consulta: str, limite: int = 5) -> list[dict]:
    if not 1 <= limite <= 10:
        raise ErrorDominio("ERROR_VALIDACION", "limite debe estar entre 1 y 10")
    parametros = urlencode({"query": consulta, "limit": limite, "fields": CAMPOS})
    encabezados = {"User-Agent": "TesisMCP/0.1 (academic discovery)", "Accept": "application/json"}
    clave_api = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if clave_api:
        encabezados["x-api-key"] = clave_api
    solicitud = Request(f"{URL_BUSQUEDA}?{parametros}", headers=encabezados)
    try:
        with urlopen(solicitud, timeout=10) as respuesta:
            carga = json.load(respuesta)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "No se pudo consultar Semantic Scholar") from error
    if not isinstance(carga, dict) or not isinstance(carga.get("data"), list):
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "Semantic Scholar devolvió una respuesta inesperada")
    articulos = []
    for articulo in carga["data"]:
        if not isinstance(articulo, dict) or not articulo.get("paperId") or not articulo.get("title"):
            continue
        identificadores_externos = articulo.get("externalIds") or {}
        acceso = articulo.get("openAccessPdf") or {}
        articulos.append({
            "proveedor": "SEMANTIC_SCHOLAR",
            "id_registro": articulo["paperId"],
            "titulo": articulo["title"],
            "autores": [autor["name"] for autor in (articulo.get("authors") or []) if isinstance(autor, dict) and autor.get("name")],
            "anio_publicacion": articulo.get("year"),
            "doi": identificadores_externos.get("DOI") if isinstance(identificadores_externos, dict) else None,
            "url_registro": articulo.get("url"),
            "url_pdf_candidata": acceso.get("url") if isinstance(acceso, dict) else None,
            "nivel_verificacion": "SOLO_METADATOS",
            "texto_completo_inspeccionado": False,
        })
    return articulos
