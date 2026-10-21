"""Mapeo y expansión geográfica dinámica para búsquedas de literatura local."""

from dataclasses import dataclass, field
import re
import unicodedata


@dataclass(frozen=True)
class AlcanceGeografico:
    region: str
    terminos_geograficos: list[str]
    instituciones_locales: list[str]
    palabras_coincidencia: list[str] = field(default_factory=list)


def _quitar_tildes(texto: str) -> str:
    return "".join(
        caracter for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    ).lower()


def _contiene_termino(texto: str, termino: str) -> bool:
    """Busca palabras o frases completas para evitar coincidencias como UNI/Universidad."""
    termino_normalizado = _quitar_tildes(termino).strip()
    return bool(termino_normalizado and re.search(
        rf"(?<!\w){re.escape(termino_normalizado)}(?!\w)", _quitar_tildes(texto)
    ))


MAPA_REGIONAL: dict[str, AlcanceGeografico] = {
    "piura": AlcanceGeografico(
        region="Piura",
        terminos_geograficos=["Piura", "Sullana", "Paita", "Talara", "Sechura", "Chulucanas", "Morropón"],
        instituciones_locales=["UDEP", "UNP", "UNFS"],
        palabras_coincidencia=["piura", "sullana", "paita", "talara", "sechura", "chulucanas", "morropon", "castilla", "catacaos", "tambogrande"],
    ),
    "lambayeque": AlcanceGeografico(
        region="Lambayeque",
        terminos_geograficos=["Lambayeque", "Chiclayo", "Ferreñafe", "Monsefú", "Pimentel"],
        instituciones_locales=["UNPRG", "USAT", "USS"],
        palabras_coincidencia=["lambayeque", "chiclayo", "ferrenafe", "pimentel", "monsefu"],
    ),
    "la libertad": AlcanceGeografico(
        region="La Libertad",
        terminos_geograficos=["La Libertad", "Trujillo", "Chepén", "Pacasmayo", "Huamachuco", "Virú"],
        instituciones_locales=["UNT", "UPAO", "UCV"],
        palabras_coincidencia=["la libertad", "trujillo", "chepen", "pacasmayo", "huamachuco", "viru"],
    ),
    "arequipa": AlcanceGeografico(
        region="Arequipa",
        terminos_geograficos=["Arequipa", "Camaná", "Caylloma", "Islay", "Mollendo", "Cerro Colorado"],
        instituciones_locales=["UNSA", "UCSP", "UCSM"],
        palabras_coincidencia=["arequipa", "camana", "caylloma", "islay", "mollendo"],
    ),
    "lima": AlcanceGeografico(
        region="Lima",
        terminos_geograficos=["Lima", "Callao", "Huacho", "Cañete", "Huaral", "Barranca"],
        instituciones_locales=["PUCP", "UNMSM", "UNI", "URP", "UPC", "ULIMA"],
        palabras_coincidencia=["lima", "callao", "huacho", "canete", "huaral", "barranca"],
    ),
    "cusco": AlcanceGeografico(
        region="Cusco",
        terminos_geograficos=["Cusco", "Urubamba", "Sicuani", "Quillabamba", "Espinar"],
        instituciones_locales=["UNSAAC", "UAC"],
        palabras_coincidencia=["cusco", "cuzco", "urubamba", "sicuani", "quillabamba", "espinar"],
    ),
    "junin": AlcanceGeografico(
        region="Junín",
        terminos_geograficos=["Junín", "Huancayo", "Tarma", "Jauja", "Chanchamayo", "Satipo"],
        instituciones_locales=["UNCP", "UPLA"],
        palabras_coincidencia=["junin", "huancayo", "tarma", "jauja", "chanchamayo", "satipo"],
    ),
    "loreto": AlcanceGeografico(
        region="Loreto",
        terminos_geograficos=["Loreto", "Iquitos", "Yurimaguas", "Nauta"],
        instituciones_locales=["UNAP"],
        palabras_coincidencia=["loreto", "iquitos", "yurimaguas", "nauta"],
    ),
}


def resolver_alcance_geografico(lugar: str | None) -> AlcanceGeografico:
    """Resuelve la jerarquía geográfica del texto libre configurado en el proyecto."""
    valor_original = (lugar or "").strip()
    if not valor_original:
        return AlcanceGeografico(
            region="Perú",
            terminos_geograficos=["Perú"],
            instituciones_locales=[],
            palabras_coincidencia=[],
        )

    valor_limpio = _quitar_tildes(valor_original)
    for clave, alcance in MAPA_REGIONAL.items():
        if _contiene_termino(valor_limpio, clave) or any(
            _contiene_termino(valor_limpio, termino) for termino in alcance.palabras_coincidencia
        ):
            return alcance

    # Fallback dinámico para localidades no indexadas explícitamente
    return AlcanceGeografico(
        region=valor_original,
        terminos_geograficos=[valor_original],
        instituciones_locales=[],
        palabras_coincidencia=[valor_limpio],
    )
