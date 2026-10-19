"""
Servidor MCP para TesisMCP (Edición Avance Capítulos 1 al 3: P01 a P12).

Inicializa el servidor MCP utilizando el SDK oficial `mcp` (`MCPServer`).
Expone el catálogo metodológico de los Capítulos 1 al 3 y las herramientas conectadas al backend.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.mcpserver import MCPServer
from mcp_server.django_bridge import configurar_django
from mcp_server.project_tools import registrar_herramientas_proyecto
from mcp_server.prompts import registrar_prompts_proyecto

configurar_django()
from thesis.step_catalogue import CATALOGO_PASOS

app = MCPServer(
    name="TesisMCP",
    description="Servidor MCP para la asistencia metodológica y supervisión de tesis universitarias (Capítulos 1 al 3).",
)

CATALOGO_MVP = CATALOGO_PASOS


@app.tool()
def estado_servidor() -> Dict[str, Any]:
    """
    Retorna el estado del servidor TesisMCP, su versión y las capacidades activas.
    Útil para comprobar que la conexión entre el cliente LLM y el servidor MCP está activa.
    """
    return {
        "estado": "ACTIVO",
        "servidor": "TesisMCP",
        "version": "0.1.0",
        "fase": "Capítulos 1 al 3 (P01 a P12 Habilitados)",
        "capitulos_disponibles": [1, 2, 3],
        "total_pasos": len(CATALOGO_PASOS),
        "motor_prompts": "ACTIVO (12 pasos P01-P12 + 3 prompts de rol)",
        "total_prompts": 15,
        "transporte_soportado": ["stdio"],
    }


@app.tool()
def listar_pasos_mvp(capitulo: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lista los pasos metodológicos del catálogo activo (P01 al P12, Capítulos 1 al 3).

    Args:
        capitulo: Filtro opcional por número de capítulo (1 al 3). Si no se especifica, lista los 12 pasos.
    """
    resultado = []
    for codigo, info in CATALOGO_PASOS.items():
        if capitulo is None or info["capitulo"] == capitulo:
            resultado.append({
                "codigo": codigo,
                "capitulo": info["capitulo"],
                "nombre": info["nombre"],
                "objetivo": info["objetivo"],
            })
    return resultado


@app.tool()
def consultar_detalle_paso(step_code: str) -> Dict[str, Any]:
    """
    Obtiene el detalle completo, objetivo y campos de entrada necesarios para ejecutar un paso (P01 a P12).

    Args:
        step_code: Código del paso (ejemplo: 'P01', 'P04', 'P06', 'P09', 'P12').
    """
    codigo_limpio = step_code.strip().upper()
    if codigo_limpio not in CATALOGO_PASOS:
        return {
            "error": True,
            "mensaje": f"El paso '{step_code}' no existe en el catálogo metodológico activo (pasos válidos: P01 a P12).",
        }

    info = CATALOGO_PASOS[codigo_limpio]
    return {
        "error": False,
        "codigo": codigo_limpio,
        "capitulo": info["capitulo"],
        "nombre": info["nombre"],
        "objetivo": info["objetivo"],
        "entradas_requeridas": info["entradas_requeridas"],
    }


registrar_herramientas_proyecto(app)
registrar_prompts_proyecto(app)


if __name__ == "__main__":
    app.run()
