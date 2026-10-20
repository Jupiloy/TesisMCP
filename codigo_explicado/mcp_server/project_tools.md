# Explicación de Código: `mcp_server/project_tools.py`

## 1. Propósito y ¿Qué hace?
Implementa y registra las **14 herramientas MCP operativas** del proyecto. Permite al agente IA o cliente MCP ejecutar acciones sobre proyectos de tesis: crear proyectos, consultar estado, registrar y explorar ideas, buscar literatura (OpenAlex, Semantic Scholar, ALICIA), ejecutar el guardado transaccional de pasos (`guardar_paso`), enviar capítulos a revisión, registrar observaciones ancladas y aprobar/reabrir entregas.

## 2. Justificación Técnica y ¿Por qué lo hace?
Cada herramienta actúa como un adaptador de transporte que traduce la invocación RPC del protocolo MCP hacia llamadas tipadas a la capa de servicios de Django. Resuelve la identidad del usuario a través de `usuario_actual()` (token SHA-256) garantizando que no se suplante la identidad de tesistas ni asesores.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Declara la función `registrar_herramientas_proyecto(app: MCPServer)`.
2. Para cada herramienta decora una función con `@app.tool()`:
   - `crear_proyecto(titulo)`: Llama a `crear_proyecto_servicio(usuario_actual(), titulo)`.
   - `obtener_estado(id_proyecto)`: Llama a `obtener_estado_proyecto_servicio(...)`.
   - `guardar_paso(id_proyecto, codigo_paso, contenido_md, salida_json, version_esperada, ...)`: Llama a `guardar_paso_servicio(...)`.
   - `enviar_capitulo(id_proyecto, numero_capitulo)`: Llama a `enviar_capitulo_servicio(...)`.
   - `observar_fragmento(id_proyecto, numero_capitulo, inicio_caracter, fin_caracter, texto, ...)`: Ancla comentario del asesor.
   - `decidir_capitulo(id_proyecto, numero_capitulo, accion, motivo)`: Ejecuta decisión del asesor.
3. Todas las excepciones de dominio (`ErrorDominio`) son capturadas y devueltas como cadenas de error descriptivas para que el LLM pueda corregir sus argumentos.

## 4. Componentes y Funciones Clave
* `registrar_herramientas_proyecto(app)`: Función de registro masivo de herramientas.
* 14 herramientas registradas con esquemas de parámetros explícitos y descripciones en español.

## 5. Relaciones con Otras Capas y Tablas
* **Autenticación:** Utiliza [`mcp_server/django_bridge.py`](./django_bridge.md).
* **Servicios:** Consume [`steps.py`](../../backend/thesis/services/steps.py), [`reviews.py`](../../backend/thesis/services/reviews.py) y [`projects.py`](../../backend/thesis/services/projects.py).
