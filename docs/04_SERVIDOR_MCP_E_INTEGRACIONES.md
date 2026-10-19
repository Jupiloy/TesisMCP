# 04. Servidor MCP (`FastMCP`), Prompts Hidratados e Integraciones Científicas

Este documento explica el funcionamiento interno del paquete [`mcp_server/`](../mcp_server/) y de las integraciones científicas en [`backend/thesis/integrations/`](../backend/thesis/integrations/).

---

## 1. Cómo Conecta el Servidor MCP con Django (`django_bridge.py`)

El protocolo MCP (*Model Context Protocol*) implementado con la librería oficial `mcp.server.fastmcp.FastMCP` puede ejecutarse dentro de un bucle de eventos asíncrono (`asyncio`). Sin embargo, el ORM de Django es síncrono por defecto y lanza `SynchronousOnlyOperation` si intentas hacer una consulta SQL directamente desde una corrutina asíncrona.

Para resolver esto limpiamente, [`mcp_server/django_bridge.py`](../mcp_server/django_bridge.py) implementa dos mecanismos:

1. **`asegurar_django()`**: Configura `sys.path`, establece `DJANGO_SETTINGS_MODULE = "config.settings"` y llama a `django.setup()` de forma idempotente solo cuando aún no ha sido inicializado.
2. **`ejecutar_sincrono(funcion, *args, **kwargs)`**:
   * Detecta si existe un bucle `asyncio` activo mediante `asyncio.get_running_loop()`.
   * Si **no** hay bucle activo (llamada directa en un script síncrono), cierra conexiones obsoletas (`close_old_connections()`) y ejecuta la función directamente.
   * Si **sí** hay un bucle asíncrono activo (como ocurre dentro de `app.call_tool()` o `app.get_prompt()` de `FastMCP`), despacha la ejecución a un hilo dedicado mediante `ThreadPoolExecutor(max_workers=1)`, garantizando seguridad transaccional con PostgreSQL.

---

## 2. Autenticación Criptográfica en MCP (`mcp_auth.py` y `TokenAccesoMcp`)

Ninguna herramienta MCP que modifique o consulte un proyecto confía en que el usuario pase un `user_id` libremente como parámetro (eso permitiría suplantación de identidad entre tesista y asesor).

En su lugar, [`backend/thesis/services/mcp_auth.py`](../backend/thesis/services/mcp_auth.py) implementa autenticación por **Token Opaco con Hash SHA-256**:

1. **Emisión (`emitir_token_acceso_mcp`)**:
   * Genera un token con prefijo identificable: `tmcp_<token_urlsafe_24>`.
   * Calcula su digest SHA-256 hexadecimal (`hashlib.sha256(token.encode("utf-8")).hexdigest()`).
   * Guarda en la tabla `tesis_token_acceso_mcp` únicamente el `prefijo_clave` (primeros 12 caracteres) y el `resumen_token` (SHA-256). El token en texto plano se devuelve **una sola vez** al crearse.
2. **Resolución (`resolver_usuario_mcp`)**:
   * Lee el token pasado a la herramienta MCP (o desde la variable de entorno `TESISMCP_TOKEN_ACCESO`).
   * Calcula su SHA-256 y busca en `TokenAccesoMcp` un registro cuyo usuario esté activo (`is_active=True`), no haya sido revocado (`revoked_at__isnull=True`) y no haya expirado (`expires_at`).
   * Actualiza la marca temporal `last_used_at` para auditoría de seguridad.

---

## 3. Catálogo de las 17 Herramientas MCP (`Tools`)

Registradas entre [`mcp_server/server.py`](../mcp_server/server.py) (3 herramientas de catálogo/diagnóstico) y [`mcp_server/project_tools.py`](../mcp_server/project_tools.py) (14 herramientas operativas):

### A. Diagnóstico y Catálogo Metodológico (`server.py`)
1. **`estado_servidor`**: Devuelve el estado `ACTIVO`, versión `0.1.0-avance-cap1-3`, capítulos disponibles `[1, 2, 3]`, total de pasos (`12`) y prompts (`15`).
2. **`listar_pasos_mvp`**: Lista los 12 pasos (`P01` a `P12`) con su título, capítulo y campos requeridos.
3. **`consultar_detalle_paso`**: Dado un `codigo_paso` (`P01`–`P12`), devuelve su definición completa; si se pide `P13` o superior, responde con error controlado indicando el alcance de los Capítulos 1 al 3.

### B. Gestión de Proyecto y Exploración Bibliográfica Inicial (`project_tools.py`)
4. **`crear_proyecto`**: Crea el proyecto en PostgreSQL, asigna al usuario autenticado como `TESISTA`, crea su `PerfilInvestigacion`, inicializa los `Capitulo` `1`, `2` y `3` en `DRAFT` y crea los 12 registros `ProgresoPaso` en `PENDING`.
5. **`obtener_estado`**: Devuelve el estado actual del proyecto, su `lock_version`, el rol del usuario y el resumen del perfil de investigación.
6. **`registrar_idea`**: Guarda la idea inicial confirmada por el tesista (con control optimista `expected_version`).
7. **`explorar_idea`**: Consulta **OpenAlex** sobre la idea registrada y devuelve metadatos bibliográficos reales advirtiendo explícitamente que los metadatos no constituyen texto completo verificado.
8. **`buscar_semantic_scholar`**: Busca artículos académicos en **Semantic Scholar** filtrables por rango de años.
9. **`buscar_antecedentes_peru`**: Busca simultáneamente tesis nacionales en **ALICIA (CONCYTEC)** y artículos con filiación institucional peruana (`country_code: PE`).

### C. Ejecución Metodológica y Flujo de Revisión Docente (`project_tools.py`)
10. **`guardar_paso`**: Valida el JSON del paso (`P01`–`P12`) contra su contrato Pydantic (`SalidaP01`–`SalidaP12`), materializa las entidades relacionales y genera una nueva `RevisionCapitulo` inmutable.
11. **`consultar_capitulo`**: Devuelve el estado de un capítulo (`1..3`), el avance de sus pasos y su documento Markdown vigente.
12. **`enviar_capitulo`**: Permite al `TESISTA` cambiar un capítulo de `DRAFT` / `CHANGES_REQUESTED` a `READY` una vez completados todos sus pasos.
13. **`asignar_asesor`**: Asigna un usuario existente como `ASESOR` activo del proyecto.
14. **`consultar_observaciones`**: Lista los comentarios de revisión (`OPEN` y `RESOLVED`) anclados al capítulo.
15. **`observar_fragmento`**: Permite al `ASESOR` anclar una observación sobre un rango exacto de caracteres (`start_offset`, `end_offset`, `quoted_text`) de la revisión vigente.
16. **`decidir_capitulo`**: Permite al `ASESOR` ejecutar `REQUEST_CHANGES`, `APPROVE` (solo si no hay observaciones `OPEN`) o `REOPEN`.
17. **`resolver_observacion`**: Permite al `ASESOR` marcar una observación como `RESOLVED`.

---

## 4. Los 15 Prompts MCP y el Motor de Hidratación (`mcp_server/prompts/`)

El servidor registra **15 prompts** en [`mcp_server/prompts/catalog.py`](../mcp_server/prompts/catalog.py):

* **12 Prompts de Pasos (`P01` a `P12`):**
  * Capítulo 1 ([`templates/chapter_1.py`](../mcp_server/prompts/templates/chapter_1.py)): `paso_p01_mapa_temas`, `paso_p02_tipo_investigacion`, `paso_p03_poblacion_ods`, `paso_p04_titulo_investigacion`, `paso_p05_alcance_investigacion`.
  * Capítulo 2 ([`templates/chapter_2.py`](../mcp_server/prompts/templates/chapter_2.py)): `paso_p06_planteamiento_problema`, `paso_p07_formulacion_problema`, `paso_p08_justificacion_investigacion`.
  * Capítulo 3 ([`templates/chapter_3.py`](../mcp_server/prompts/templates/chapter_3.py)): `paso_p09_objetivos_matriz`, `paso_p10_preguntas_hipotesis`, `paso_p11_definicion_variables`, `paso_p12_operacionalizacion`.
* **3 Prompts de Roles Especializados ([`prompts/roles.py`](../mcp_server/prompts/roles.py)):**
  * `rol_asesor_metodologico`: Configura al LLM como asesor metodológico riguroso.
  * `rol_investigador_grounded`: Configura al LLM bajo la regla de cero alucinaciones bibliográficas.
  * `rol_revisor_contratos`: Configura al LLM como auditor de esquemas JSON antes de invocar `guardar_paso`.

Cuando cualquiera de los 12 prompts recibe un `project_id`, [`hydration.py`](../mcp_server/prompts/hydration.py) consulta PostgreSQL en tiempo real e inyecta el título del proyecto, su `lock_version`, el estado de su `PerfilInvestigacion`, las filas actuales de su `FilaConsistencia`, sus `VariableInvestigacion` y los últimos pasos completados.
