"""Agregador central de plantillas de prompts metodológicos (Capítulos 1 al 3: P01 a P12)."""

from typing import Any

from mcp_server.prompts.templates.chapter_1 import CHAPTER_1_TEMPLATES
from mcp_server.prompts.templates.chapter_2 import CHAPTER_2_TEMPLATES
from mcp_server.prompts.templates.chapter_3 import CHAPTER_3_TEMPLATES

TEMPLATES_POR_PASO: dict[str, dict[str, Any]] = {
    **CHAPTER_1_TEMPLATES,
    **CHAPTER_2_TEMPLATES,
    **CHAPTER_3_TEMPLATES,
}

__all__ = ["TEMPLATES_POR_PASO"]
