"""Adaptador HTTP: nunca convierte metadatos en evidencia de texto completo."""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errores import ErrorDominio


URL_TRABAJOS_OPENALEX = "https://api.openalex.org/works"
PATRON_ID_TRABAJO = re.compile(r"^(?:https://openalex\.org/)?(W[1-9][0-9]*)$")


def _solicitar_json(url: str) -> dict:
    solicitud = Request(url, headers={"User-Agent": "TesisMCP/0.1 (academic discovery)", "Accept": "application/json"})
    try:
        with urlopen(solicitud, timeout=10) as respuesta:
            carga = json.load(respuesta)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "No se pudo consultar el registro en OpenAlex") from error
    if not isinstance(carga, dict):
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "OpenAlex devolvió una respuesta inesperada")
    return carga


def obtener_trabajo_openalex(id_openalex: str) -> dict:
    coincidencia = PATRON_ID_TRABAJO.fullmatch(id_openalex.strip())
    if not coincidencia:
        raise ErrorDominio("ERROR_VALIDACION", "Identificador OpenAlex inválido")
    id_trabajo = coincidencia.group(1)
    parametros = {}
    correo = os.getenv("OPENALEX_CONTACT_EMAIL", "").strip()
    if correo:
        parametros["mailto"] = correo
    sufijo = f"?{urlencode(parametros)}" if parametros else ""
    trabajo = _solicitar_json(f"{URL_TRABAJOS_OPENALEX}/{id_trabajo}{sufijo}")
    normalizado = _normalizar_trabajo(trabajo)
    if normalizado is None or normalizado["id_openalex"] != f"https://openalex.org/{id_trabajo}":
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "OpenAlex no devolvió el trabajo solicitado")
    return normalizado


def buscar_trabajos_openalex(consulta: str, limite: int = 5) -> list[dict]:
    if not 1 <= limite <= 10:
        raise ErrorDominio("ERROR_VALIDACION", "limite debe estar entre 1 y 10")
    parametros = {"search": consulta, "per_page": limite}
    correo = os.getenv("OPENALEX_CONTACT_EMAIL", "").strip()
    if correo:
        parametros["mailto"] = correo
    carga = _solicitar_json(f"{URL_TRABAJOS_OPENALEX}?{urlencode(parametros)}")

    if not isinstance(carga, dict) or not isinstance(carga.get("results"), list):
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "OpenAlex devolvió una respuesta inesperada")

    trabajos = []
    for trabajo in carga["results"]:
        normalizado = _normalizar_trabajo(trabajo)
        if normalizado:
            trabajos.append(normalizado)
    return trabajos


def _normalizar_trabajo(trabajo: dict) -> dict | None:
    if not isinstance(trabajo, dict) or not trabajo.get("id") or not trabajo.get("title"):
        return None
    autores = []
    for autoria in trabajo.get("authorships") or []:
        if isinstance(autoria, dict):
            autor = autoria.get("author") or {}
            if isinstance(autor, dict) and autor.get("display_name"):
                autores.append(autor["display_name"])
    ubicacion = trabajo.get("best_oa_location") or {}
    ubicacion_principal = trabajo.get("primary_location") or {}
    if not isinstance(ubicacion, dict):
        ubicacion = {}
    if not isinstance(ubicacion_principal, dict):
        ubicacion_principal = {}
    return {
        "id_openalex": trabajo["id"], "titulo": trabajo["title"], "autores": autores,
        "anio_publicacion": trabajo.get("publication_year"), "doi": trabajo.get("doi"),
        "url_registro": trabajo["id"],
        "url_pagina": ubicacion.get("landing_page_url") or ubicacion_principal.get("landing_page_url"),
        "url_pdf": ubicacion.get("pdf_url"), "retractado_openalex": trabajo.get("is_retracted"),
        "nivel_verificacion": "SOLO_METADATOS",
        "texto_completo_inspeccionado": False,
    }
