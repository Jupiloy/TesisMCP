"""
Servidor MCP para TesisMCP (Edición Avance Capítulos 1 al 3: P01 a P12).

Inicializa el servidor MCP utilizando el SDK oficial `mcp` (`MCPServer`).
Expone el catálogo metodológico de los Capítulos 1 al 3 y las herramientas conectadas al backend.
"""

import sys
from pathlib import Path
from typing import Any

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from mcp.server.mcpserver import MCPServer
from mcp_server.puente_django import configurar_django
from mcp_server.herramientas_proyecto import registrar_herramientas_proyecto
from mcp_server.prompts import registrar_prompts_proyecto

configurar_django()
from thesis.catalogo_pasos import CATALOGO_PASOS

app = MCPServer(
    name="TesisMCP",
    description="Servidor MCP para la asistencia metodológica y supervisión de tesis universitarias (Capítulos 1 al 3).",
)

@app.tool()
def estado_servidor() -> dict[str, Any]:
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
def listar_pasos_mvp(capitulo: int | None = None) -> list[dict[str, Any]]:
    """
    Lista los pasos metodológicos del catálogo activo (P01 al P12, Capítulos 1 al 3).

    Args:
        capitulo: Filtro opcional por número de capítulo (1 al 3). Si no se especifica, lista los 12 pasos.
    """
    resultado = []
    for codigo, informacion in CATALOGO_PASOS.items():
        if capitulo is None or informacion["capitulo"] == capitulo:
            resultado.append({
                "codigo": codigo,
                "capitulo": informacion["capitulo"],
                "nombre": informacion["nombre"],
                "objetivo": informacion["objetivo"],
            })
    return resultado


@app.tool()
def consultar_detalle_paso(codigo_paso: str) -> dict[str, Any]:
    """
    Obtiene el detalle completo, objetivo y campos de entrada necesarios para ejecutar un paso (P01 a P12).

    Args:
        codigo_paso: Código del paso (ejemplo: 'P01', 'P04', 'P06', 'P09', 'P12').
    """
    codigo_limpio = codigo_paso.strip().upper()
    if codigo_limpio not in CATALOGO_PASOS:
        return {
            "codigo": "PASO_NO_ENCONTRADO",
            "mensaje": f"El paso '{codigo_paso}' no existe en el catálogo metodológico activo (pasos válidos: P01 a P12).",
            "detalle": "Consulta el catálogo de pasos antes de solicitar el detalle",
        }

    informacion = CATALOGO_PASOS[codigo_limpio]
    return {
        "codigo": codigo_limpio,
        "capitulo": informacion["capitulo"],
        "nombre": informacion["nombre"],
        "objetivo": informacion["objetivo"],
        "entradas_requeridas": informacion["entradas_requeridas"],
    }


registrar_herramientas_proyecto(app)
registrar_prompts_proyecto(app)


if __name__ == "__main__":
    app.run()
