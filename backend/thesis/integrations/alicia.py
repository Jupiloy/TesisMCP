"""Adaptador para la API REST de ALICIA (CONCYTEC).

Devuelve exclusivamente metadatos normalizados (SOLO_METADATOS); no afirma inspección de texto completo.
"""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from thesis.services.errores import ErrorDominio

URL_API_ALICIA = "https://alicia.concytec.gob.pe/vufind/api/v1/search"


def _solicitar_json(url: str) -> dict:
    solicitud = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(solicitud, timeout=12) as respuesta:
            carga = json.load(respuesta)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "No se pudo consultar el catálogo de ALICIA CONCYTEC") from error
    if not isinstance(carga, dict):
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "ALICIA CONCYTEC devolvió una respuesta inesperada")
    return carga


def _extraer_autores(autores_originales: dict | list | None) -> list[str]:
    if not isinstance(autores_originales, dict):
        return []
    nombres = []
    principales = autores_originales.get("primary") or {}
    if isinstance(principales, dict):
        nombres.extend(list(principales.keys()))
    # Los nombres secundarios pueden corresponder a asesores o colaboradores.
    return [nombre.strip() for nombre in nombres if nombre and nombre.strip()]


def _extraer_identificador_handle(direcciones: list[dict] | None) -> str | None:
    if not isinstance(direcciones, list):
        return None
    for entrada in direcciones:
        if isinstance(entrada, dict) and entrada.get("url"):
            direccion = entrada["url"]
            if "hdl.handle.net" in direccion or "handle" in direccion or "repositorio" in direccion:
                return direccion
    return direcciones[0].get("url") if direcciones and isinstance(direcciones[0], dict) else None


def _normalizar_registro_alicia(registrar_resultado: dict) -> dict | None:
    if not isinstance(registrar_resultado, dict) or not registrar_resultado.get("title"):
        return None

    direcciones = registrar_resultado.get("urls") or []
    identificador_handle = _extraer_identificador_handle(direcciones)
    autores = _extraer_autores(registrar_resultado.get("authors"))

    # Intentar obtener el año de publicación
    anio = None
    fechas_publicacion = registrar_resultado.get("publicationDates") or registrar_resultado.get("dcDateIssued") or []
    primera_fecha = fechas_publicacion[0] if isinstance(fechas_publicacion, list) and fechas_publicacion else fechas_publicacion
    coincidencia = re.search(r"\b(?:19|20)\d{2}\b", str(primera_fecha)) if primera_fecha else None
    if coincidencia:
        anio = int(coincidencia.group())

    otorgante = registrar_resultado.get("thesisDegreeGrantor")
    if isinstance(otorgante, list) and otorgante:
        institucion = str(otorgante[0])
    else:
        publicador = registrar_resultado.get("institution") or registrar_resultado.get("dcPublisher")
        institucion = str(publicador[0] if isinstance(publicador, list) and publicador else publicador) if publicador else None

    resumenes = registrar_resultado.get("dcDescriptionAbstract") or []
    resumen = resumenes[0] if isinstance(resumenes, list) and resumenes else (
        resumenes if isinstance(resumenes, str) else ""
    )

    return {
        "origen_fuente": "ALICIA_CONCYTEC",
        "id_registro": registrar_resultado.get("id"),
        "titulo": registrar_resultado["title"].strip(),
        "autores": autores,
        "anio_publicacion": anio,
        "institucion": institucion,
        "url_handle": identificador_handle,
        "url_pagina": identificador_handle,
        "resumen": resumen,
        "nivel_verificacion": "SOLO_METADATOS",
        "texto_completo_inspeccionado": False,
    }


def buscar_tesis_alicia(consulta: str, instituciones: list[str] | None = None, limite: int = 5) -> list[dict]:
    """Busca tesis en ALICIA (CONCYTEC) aplicando opcionalmente filtros institucionales."""
    if not 1 <= limite <= 20:
        raise ErrorDominio("ERROR_VALIDACION", "limite debe estar entre 1 y 20")

    consulta = consulta.strip()
    if not consulta:
        raise ErrorDominio("ERROR_VALIDACION", "La consulta de búsqueda no puede estar vacía")

    parametros = [("lookfor", consulta), ("limit", str(limite))]
    if instituciones:
        for institucion in instituciones:
            parametros.append(("filter[]", f'institution:"{institucion}"'))

    url = f"{URL_API_ALICIA}?{urlencode(parametros)}"
    carga = _solicitar_json(url)

    resultados = []
    for registro_original in carga.get("records") or []:
        normalizado = _normalizar_registro_alicia(registro_original)
        if normalizado:
            resultados.append(normalizado)
    return resultados
