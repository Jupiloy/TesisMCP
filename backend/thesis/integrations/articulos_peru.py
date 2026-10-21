"""Adaptador para buscar artículos con al menos una filiación institucional peruana.

La clasificación de OpenAlex y el país de filiación no acreditan revisión por pares.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errores import ErrorDominio

URL_OPENALEX_PERU = "https://api.openalex.org/works"


def buscar_articulos_afiliacion_peru(consulta: str, limite: int = 5) -> list[dict]:
    """Busca trabajos de tipo artículo con filiación en instituciones peruanas."""
    if not 1 <= limite <= 10:
        raise ErrorDominio("ERROR_VALIDACION", "limite debe estar entre 1 y 10")

    consulta = consulta.strip()
    if not consulta:
        raise ErrorDominio("ERROR_VALIDACION", "La consulta de búsqueda no puede estar vacía")

    parametros = {
        "search": consulta,
        "filter": "authorships.institutions.country_code:PE",
        "per_page": limite,
    }
    url = f"{URL_OPENALEX_PERU}?{urlencode(parametros)}"
    solicitud = Request(
        url,
        headers={"User-Agent": "TesisMCP/0.1 (academic discovery with Peruvian affiliation)", "Accept": "application/json"},
    )
    try:
        with urlopen(solicitud, timeout=12) as respuesta:
            carga = json.load(respuesta)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "No se pudo consultar el catálogo de artículos peruanos") from error

    resultados = []
    for trabajo in carga.get("results") or []:
        if not isinstance(trabajo, dict) or not trabajo.get("title") or trabajo.get("type") != "article":
            continue

        autores = []
        instituciones = []
        for autoria in trabajo.get("authorships") or []:
            if isinstance(autoria, dict):
                autor = autoria.get("author") or {}
                if isinstance(autor, dict) and autor.get("display_name"):
                    autores.append(autor["display_name"])
                for institucion in autoria.get("institutions") or []:
                    if isinstance(institucion, dict) and institucion.get("display_name"):
                        instituciones.append(institucion["display_name"])

        ubicacion = trabajo.get("best_oa_location") or {}
        pagina = ubicacion.get("landing_page_url") or (trabajo.get("primary_location") or {}).get("landing_page_url") or trabajo.get("id")

        resultados.append({
            "origen_fuente": "ARTICULO_CON_FILIACION_PERUANA",
            "id_registro": trabajo.get("id"),
            "titulo": trabajo["title"].strip(),
            "autores": autores,
            "anio_publicacion": trabajo.get("publication_year"),
            "doi": trabajo.get("doi"),
            "instituciones": list(set(instituciones)),
            "url_pagina": pagina,
            "url_pdf": ubicacion.get("pdf_url"),
            "revision_pares_verificada": False,
            "nivel_verificacion": "SOLO_METADATOS",
            "texto_completo_inspeccionado": False,
        })
    return resultados
