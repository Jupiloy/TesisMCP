# Explicación de Código: `mcp_server/server.py`

## 1. Propósito y ¿Qué hace?
Es el **punto de entrada principal del Servidor Model Context Protocol (MCP)** de TesisMCP. Instancia el objeto `MCPServer("tesismcp-server")` utilizando el SDK oficial `mcp`, registra las herramientas de catálogo y diagnóstico (`estado_servidor`, `listar_pasos_mvp`, `consultar_detalle_paso`), monta las herramientas operativas de proyectos y registra los 15 prompts MCP dinámicos.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Protocolo Estándar Abierto:** Permite que cualquier entorno de desarrollo o agente de IA compatible con MCP (Claude Desktop, Cursor, IDEs modernos) consuma las capacidades del sistema como herramientas nativas (*tools*) y plantillas de contexto (*prompts*).
* **Desacoplamiento Modular:** Separa las herramientas de inspección y estado general de las herramientas que modifican proyectos específicos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Crea `app = MCPServer("tesismcp-server")`.
2. Define y registra con `@app.tool()`:
   - `estado_servidor()`: Devuelve estado `ACTIVO`, versión `0.1.0`, capítulos disponibles `[1, 2, 3]`, total de pasos (`12`) y prompts (`15`).
   - `listar_pasos_mvp()`: Consulta `CATALOGO_PASOS` y retorna la lista ordenada de `P01` a `P12`.
   - `consultar_detalle_paso(codigo_paso)`: Devuelve la definición completa del paso; si se consulta `P13` o superior, devuelve un error controlado de alcance.
3. Invoca `registrar_herramientas_proyecto(app)` para anexar las 14 herramientas de `project_tools.py`.
4. Invoca `registrar_prompts(app)` para montar los 15 prompts dinámicos.
5. Provee el bloque `if __name__ == '__main__': app.run()` usando transporte `stdio`.

## 4. Componentes y Funciones Clave
* `app = MCPServer("tesismcp-server")`: Instancia central del servidor MCP.
* `estado_servidor()`: Herramienta de telemetría y diagnóstico.
* `listar_pasos_mvp()`: Herramienta de catálogo de pasos activos.
* `consultar_detalle_paso(...)`: Herramienta de detalle metodológico.

## 5. Relaciones con Otras Capas y Tablas
* **Catálogo:** Lee [`backend/thesis/step_catalogue.py`](../../backend/thesis/step_catalogue.py).
* **Módulos MCP:** Agrupa [`project_tools.py`](./project_tools.md) y [`prompts/catalog.py`](./prompts/catalog.md).
* **Simulación:** Ejecutado por [`mcp_server/test_local.py`](./test_local.md).
