from thesis.integrations.openalex import buscar_trabajos_openalex
from thesis.services.proyectos import obtener_estado_proyecto


PREGUNTAS_ORIENTADORAS = [
    "¿Qué área o situación te interesa investigar?",
    "¿A qué población o institución podrías acceder?",
    "¿En qué lugar y periodo observarías el problema?",
]


def explorar_idea_servicio(usuario, id_proyecto, *, proveedor_busqueda=buscar_trabajos_openalex) -> dict:
    estado = obtener_estado_proyecto(usuario, id_proyecto)
    idea = estado["idea_provisional"]
    if not idea:
        return {
            "id_proyecto": estado["id_proyecto"],
            "estado_busqueda": "REQUIERE_IDEA",
            "preguntas_orientadoras": PREGUNTAS_ORIENTADORAS,
            "trabajos": [],
            "aviso": "Todavía no hay una idea provisional. Las preguntas ayudan a iniciar la exploración.",
        }
    trabajos = proveedor_busqueda(idea)
    return {
        "id_proyecto": estado["id_proyecto"],
        "estado_busqueda": "RESULTADOS" if trabajos else "SIN_RESULTADOS",
        "preguntas_orientadoras": [],
        "trabajos": trabajos,
        "aviso": (
            "Estos registros proceden de metadatos de OpenAlex. No se ha leído su texto completo "
            "ni se ha demostrado que describan el problema local."
        ),
    }
