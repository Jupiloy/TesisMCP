"""Paquete del servidor MCP de TesisMCP.

La aplicación se importa explícitamente desde :mod:`mcp_server.server`. Mantener
este ``__init__`` libre de efectos evita que ``python -m mcp_server.server``
cargue y registre el servidor dos veces antes de iniciar el transporte stdio.
"""
