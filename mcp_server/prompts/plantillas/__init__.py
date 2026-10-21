"""Agregador central de plantillas de prompts metodológicos (Capítulos 1 al 3: P01 a P12)."""

from typing import Any

from mcp_server.prompts.plantillas.capitulo_1 import PLANTILLAS_CAPITULO_1
from mcp_server.prompts.plantillas.capitulo_2 import PLANTILLAS_CAPITULO_2
from mcp_server.prompts.plantillas.capitulo_3 import PLANTILLAS_CAPITULO_3

PLANTILLAS_POR_PASO: dict[str, dict[str, Any]] = {
    **PLANTILLAS_CAPITULO_1,
    **PLANTILLAS_CAPITULO_2,
    **PLANTILLAS_CAPITULO_3,
}

__all__ = ["PLANTILLAS_POR_PASO"]
