# 04. Servidor MCP (`MCPServer`), Prompts Hidratados e Integraciones Científicas

Este documento explica el funcionamiento interno del paquete [`mcp_server/`](../mcp_server/) y de las integraciones científicas en [`backend/thesis/integrations/`](../backend/thesis/integrations/).

---

## 1. Cómo Conecta el Servidor MCP con Django (`puente_django.py`)

El protocolo MCP (*Model Context Protocol*) está implementado con `mcp.server.mcpserver.MCPServer`, perteneciente al SDK oficial `mcp`. Las herramientas registradas son funciones síncronas que delegan en servicios Django transaccionales.

[`mcp_server/puente_django.py`](../mcp_server/puente_django.py) implementa dos puntos concretos:

1. **`configurar_django()`**: agrega `backend/` a `sys.path`, establece `DJANGO_SETTINGS_MODULE`, habilita el uso síncrono controlado del ORM en el proceso MCP y llama a `django.setup()` de forma idempotente.
2. **`usuario_actual()`**: toma `TESISMCP_MCP_TOKEN` del entorno y lo resuelve con `usuario_desde_token()`. Si falta, está vencido o fue revocado, la operación falla de forma cerrada.

---

## 2. Autenticación Criptográfica en MCP (`mcp_auth.py` y `TokenAccesoMcp`)

Ninguna herramienta MCP que modifique o consulte un proyecto confía en que el usuario pase un `user_id` libremente como parámetro (eso permitiría suplantación de identidad entre tesista y asesor).

En su lugar, [`backend/thesis/services/autenticacion_mcp.py`](../backend/thesis/services/autenticacion_mcp.py) implementa autenticación por **Token Opaco con Hash SHA-256**:

1. **Emisión (`emitir_token`)**:
   * Genera 48 bytes aleatorios con `secrets.token_urlsafe(48)`.
   * Calcula su digest SHA-256 hexadecimal (`hashlib.sha256(raw.encode()).hexdigest()`).
   * Guarda únicamente `hash_token`, usuario, expiración, revocación y fecha de creación. El token en texto plano se devuelve una sola vez.
2. **Resolución (`usuario_desde_token`)**:
   * Lee el token desde la variable de entorno `TESISMCP_MCP_TOKEN`.
   * Calcula su SHA-256 y busca en `TokenAccesoMcp` un registro cuyo usuario esté activo (`is_active=True`), no haya sido revocado (`revoked_at__isnull=True`) y no haya expirado (`expires_at`).

---

## 3. Catálogo de las 17 Herramientas MCP (`Tools`)

Registradas entre [`mcp_server/server.py`](../mcp_server/server.py) (3 herramientas de catálogo/diagnóstico) y [`mcp_server/herramientas_proyecto.py`](../mcp_server/herramientas_proyecto.py) (14 herramientas operativas):

### A. Diagnóstico y Catálogo Metodológico (`server.py`)
1. **`estado_servidor`**: Devuelve el estado `ACTIVO`, versión `0.1.0`, capítulos disponibles `[1, 2, 3]`, total de pasos (`12`) y prompts (`15`).
2. **`listar_pasos_mvp`**: Lista los 12 pasos (`P01` a `P12`) con su título, capítulo y campos requeridos.
3. **`consultar_detalle_paso`**: Dado un `codigo_paso` (`P01`–`P12`), devuelve su definición completa; si se pide `P13` o superior, responde con error controlado indicando el alcance de los Capítulos 1 al 3.

### B. Gestión de Proyecto y Exploración Bibliográfica Inicial (`herramientas_proyecto.py`)
4. **`crear_proyecto`**: Crea el proyecto en PostgreSQL, asigna al usuario autenticado como `TESISTA` y crea su `PerfilInvestigacion`. Los registros `Capitulo` y `ProgresoPaso` se materializan de forma diferida conforme se ejecutan los pasos.
5. **`obtener_estado`**: Devuelve el estado actual del proyecto, su `lock_version`, el rol del usuario y el resumen del perfil de investigación.
6. **`registrar_idea`**: Guarda la idea inicial confirmada por el tesista (con control optimista `version_esperada`).
7. **`explorar_idea`**: Consulta **OpenAlex** sobre la idea registrada y devuelve metadatos bibliográficos reales advirtiendo explícitamente que los metadatos no constituyen texto completo verificado.
8. **`buscar_semantic_scholar`**: Busca artículos académicos en **Semantic Scholar** filtrables por rango de años.
9. **`buscar_antecedentes_peru`**: Busca simultáneamente tesis nacionales en **ALICIA (CONCYTEC)** y artículos con filiación institucional peruana (`country_code: PE`).

### C. Ejecución Metodológica y Flujo de Revisión Docente (`herramientas_proyecto.py`)
10. **`guardar_paso`**: Valida el JSON del paso (`P01`–`P12`) contra su contrato Pydantic (`SalidaP01`–`SalidaP12`), materializa las entidades relacionales y genera una nueva `RevisionCapitulo` inmutable.
11. **`consultar_capitulo`**: Devuelve el estado de un capítulo (`1..3`), el avance de sus pasos y su documento Markdown vigente.
12. **`enviar_capitulo`**: Permite al `TESISTA` cambiar un capítulo de `BORRADOR` / `CON_OBSERVACIONES` a `EN_REVISION` una vez completados todos sus pasos.
13. **`asignar_asesor`**: Asigna un usuario existente como `ASESOR` activo del proyecto.
14. **`consultar_observaciones`**: Lista los comentarios de revisión (`ABIERTA` y `RESUELTA`) anclados al capítulo.
15. **`observar_fragmento`**: Permite al `ASESOR` anclar una observación sobre un rango exacto de caracteres (`inicio_caracter`, `fin_caracter`, `texto_seleccionado`) de la revisión vigente.
16. **`decidir_capitulo`**: Permite al `ASESOR` ejecutar `SOLICITAR_CAMBIOS`, `APROBAR` (solo si no hay observaciones `ABIERTA`) o `REABRIR`.
17. **`resolver_observacion`**: Permite al `ASESOR` marcar una observación como `RESUELTA`.

---

## 4. Los 15 Prompts MCP y el Motor de Hidratación (`mcp_server/prompts/`)

El servidor registra **15 prompts** en [`mcp_server/prompts/catalogo.py`](../mcp_server/prompts/catalogo.py):

* **12 Prompts de Pasos (`P01` a `P12`):**
  * Capítulo 1 ([`templates/capitulo_1.py`](../mcp_server/prompts/plantillas/capitulo_1.py)): `paso_p01_mapa_temas`, `paso_p02_tipo_investigacion`, `paso_p03_poblacion_ods`, `paso_p04_titulo_investigacion`, `paso_p05_alcance_investigacion`.
  * Capítulo 2 ([`templates/capitulo_2.py`](../mcp_server/prompts/plantillas/capitulo_2.py)): `paso_p06_planteamiento_problema`, `paso_p07_formulacion_problema`, `paso_p08_justificacion_investigacion`.
  * Capítulo 3 ([`templates/capitulo_3.py`](../mcp_server/prompts/plantillas/capitulo_3.py)): `paso_p09_objetivos_matriz`, `paso_p10_preguntas_hipotesis`, `paso_p11_definicion_variables`, `paso_p12_operacionalizacion`.
* **3 Prompts de Roles Especializados ([`prompts/roles.py`](../mcp_server/prompts/roles.py)):**
  * `rol_asesor_metodologico`: Configura al LLM como asesor metodológico riguroso.
  * `rol_investigador_grounded`: Configura al LLM bajo la regla de cero alucinaciones bibliográficas.
  * `rol_revisor_contratos`: Configura al LLM como auditor de esquemas JSON antes de invocar `guardar_paso`.

Cuando cualquiera de los 12 prompts recibe un `id_proyecto`, [`hydration.py`](../mcp_server/prompts/hidratacion.py) consulta PostgreSQL en tiempo real e inyecta el título del proyecto, su `version_estado`, el estado de su `PerfilInvestigacion`, las filas actuales de su `FilaConsistencia`, sus `VariableInvestigacion` y los últimos pasos completados.
