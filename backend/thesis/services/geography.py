"""Mapeo y expansión geográfica dinámica para búsquedas de literatura local."""

from dataclasses import dataclass, field
import re
import unicodedata


@dataclass(frozen=True)
class AlcanceGeografico:
    region: str
    geographic_terms: list[str]
    local_institutions: list[str]
    match_keywords: list[str] = field(default_factory=list)


def _quitar_tildes(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    ).lower()


def _contiene_termino(text: str, term: str) -> bool:
    """Busca palabras o frases completas para evitar coincidencias como UNI/Universidad."""
    normalized_term = _quitar_tildes(term).strip()
    return bool(normalized_term and re.search(
        rf"(?<!\w){re.escape(normalized_term)}(?!\w)", _quitar_tildes(text)
    ))


REGIONAL_MAP: dict[str, AlcanceGeografico] = {
    "piura": AlcanceGeografico(
        region="Piura",
        geographic_terms=["Piura", "Sullana", "Paita", "Talara", "Sechura", "Chulucanas", "Morropón"],
        local_institutions=["UDEP", "UNP", "UNFS"],
        match_keywords=["piura", "sullana", "paita", "talara", "sechura", "chulucanas", "morropon", "castilla", "catacaos", "tambogrande"],
    ),
    "lambayeque": AlcanceGeografico(
        region="Lambayeque",
        geographic_terms=["Lambayeque", "Chiclayo", "Ferreñafe", "Monsefú", "Pimentel"],
        local_institutions=["UNPRG", "USAT", "USS"],
        match_keywords=["lambayeque", "chiclayo", "ferrenafe", "pimentel", "monsefu"],
    ),
    "la libertad": AlcanceGeografico(
        region="La Libertad",
        geographic_terms=["La Libertad", "Trujillo", "Chepén", "Pacasmayo", "Huamachuco", "Virú"],
        local_institutions=["UNT", "UPAO", "UCV"],
        match_keywords=["la libertad", "trujillo", "chepen", "pacasmayo", "huamachuco", "viru"],
    ),
    "arequipa": AlcanceGeografico(
        region="Arequipa",
        geographic_terms=["Arequipa", "Camaná", "Caylloma", "Islay", "Mollendo", "Cerro Colorado"],
        local_institutions=["UNSA", "UCSP", "UCSM"],
        match_keywords=["arequipa", "camana", "caylloma", "islay", "mollendo"],
    ),
    "lima": AlcanceGeografico(
        region="Lima",
        geographic_terms=["Lima", "Callao", "Huacho", "Cañete", "Huaral", "Barranca"],
        local_institutions=["PUCP", "UNMSM", "UNI", "URP", "UPC", "ULIMA"],
        match_keywords=["lima", "callao", "huacho", "canete", "huaral", "barranca"],
    ),
    "cusco": AlcanceGeografico(
        region="Cusco",
        geographic_terms=["Cusco", "Urubamba", "Sicuani", "Quillabamba", "Espinar"],
        local_institutions=["UNSAAC", "UAC"],
        match_keywords=["cusco", "cuzco", "urubamba", "sicuani", "quillabamba", "espinar"],
    ),
    "junin": AlcanceGeografico(
        region="Junín",
        geographic_terms=["Junín", "Huancayo", "Tarma", "Jauja", "Chanchamayo", "Satipo"],
        local_institutions=["UNCP", "UPLA"],
        match_keywords=["junin", "huancayo", "tarma", "jauja", "chanchamayo", "satipo"],
    ),
    "loreto": AlcanceGeografico(
        region="Loreto",
        geographic_terms=["Loreto", "Iquitos", "Yurimaguas", "Nauta"],
        local_institutions=["UNAP"],
        match_keywords=["loreto", "iquitos", "yurimaguas", "nauta"],
    ),
}


def resolver_alcance_geografico(place: str | None) -> AlcanceGeografico:
    """Resuelve la jerarquía geográfica del texto libre configurado en el proyecto."""
    raw = (place or "").strip()
    if not raw:
        return AlcanceGeografico(
            region="Perú",
            geographic_terms=["Perú"],
            local_institutions=[],
            match_keywords=[],
        )

    clean = _quitar_tildes(raw)
    for key, scope in REGIONAL_MAP.items():
        if _contiene_termino(clean, key) or any(_contiene_termino(clean, term) for term in scope.match_keywords):
            return scope

    # Fallback dinámico para localidades no indexadas explícitamente
    return AlcanceGeografico(
        region=raw,
        geographic_terms=[raw],
        local_institutions=[],
        match_keywords=[clean],
    )
