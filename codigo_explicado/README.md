# Guía Pedagógica y Mapa del Código Fuente (`V1/codigo_explicado/`)

Bienvenido a la documentación explicativa **archivo por archivo** del proyecto **TesisMCP (Versión Reducida V1: Capítulos 1 al 3)**.

Esta carpeta reproduce la estructura física del código fuente. Cada archivo Markdown (`.md`) desglosa un componente sustantivo bajo una plantilla pedagógica estricta de 5 secciones:
1. **Propósito y ¿Qué hace?:** Rol y responsabilidades dentro del sistema.
2. **Justificación Técnica y ¿Por qué lo hace?:** Problema metodológico o patrón de software que fundamenta su diseño.
3. **Mecanismo Interno y ¿Cómo lo hace?:** Flujo de ejecución paso a paso, validaciones y algoritmos.
4. **Componentes y Funciones Clave:** Métodos, clases y firmas esenciales.
5. **Relaciones con Otras Capas y Tablas:** Interacción con modelos, servicios, base de datos y clientes.

---

## 🗺️ Mapa de Navegación de la Estructura

### 1. Núcleo Backend (`backend/`)
* [**`backend/manage.md`**](./backend/manage.md): Punto de entrada CLI para tareas administrativas de Django.
* **Configuración del Sistema (`backend/config/`):**
  * [**`config/settings.md`**](./backend/config/settings.md): Configuración de PostgreSQL 16 (puerto 5434), seguridad y Django Ninja.
  * [**`config/api.md`**](./backend/config/api.md): Instancia raíz de `NinjaAPI`, endpoint `/health/` y enrutador REST.
  * [**`config/urls.md`**](./backend/config/urls.md): Enrutamiento URL raíz de endpoints web y administrativos.
* **Dominio Metodológico Base (`backend/thesis/`):**
  * [**`thesis/admin.md`**](./backend/thesis/admin.md): Panel de administración con protección *append-only* en revisiones.
  * [**`thesis/step_catalogue.md`**](./backend/thesis/step_catalogue.md): Catálogo canónico de los 12 pasos metodológicos (`P01`–`P12`).
  * [**`thesis/management/issue_mcp_token.md`**](./backend/thesis/management/issue_mcp_token.md): Comando CLI para emitir tokens opacos SHA-256.

### 2. Capa de Persistencia Relacional (`backend/thesis/models/`)
* [**`models/accounts.md`**](./backend/thesis/models/accounts.md): Autenticación de `Usuario` y `TokenAccesoMcp` (hash SHA-256).
* [**`models/projects.md`**](./backend/thesis/models/projects.md): `Proyecto` y `ParticipanteProyecto` (roles `OWNER` y `ADVISOR`).
* [**`models/research.md`**](./backend/thesis/models/research.md): `PerfilInvestigacion` (con `lock_version`), `FilaConsistencia`, variables, dimensiones e indicadores.
* [**`models/chapters.md`**](./backend/thesis/models/chapters.md): `Capitulo` (1..3), `RevisionCapitulo` (inmutable), `ComentarioRevision` (anclado) y `EventoRevision`.
* [**`models/traduccion_espanol.md`**](./backend/thesis/models/traduccion_espanol.md): Mapeo de `COLUMNAS_FISICAS` y alias públicos de las 17 tablas `tesis_*`.

### 3. Capa de Servicios de Dominio (`backend/thesis/services/`)
* [**`services/step_contracts.md`**](./backend/thesis/services/step_contracts.md): Contratos Pydantic V2 (`SalidaP01` a `SalidaP12`) con `extra="forbid"`.
* [**`services/steps.md`**](./backend/thesis/services/steps.md): Orquestación transaccional `guardar_paso_servicio` con control OCC (`lock_version`).
* [**`services/reviews.md`**](./backend/thesis/services/reviews.md): Máquina de estados de revisión del asesor y observaciones ancladas.
* [**`services/projects.md`**](./backend/thesis/services/projects.md): Inicialización atómica de proyecto y perfil.
* [**`services/mcp_auth.md`**](./backend/thesis/services/mcp_auth.md): Emisión y validación segura de tokens opacos.
* [**`services/discovery_peru.md`**](./backend/thesis/services/discovery_peru.md): Búsqueda en repositorio ALICIA CONCYTEC y filiación peruana.
* [**`services/geography.md`**](./backend/thesis/services/geography.md): Inferencia determinista de ámbito geográfico de investigación.
* [**`services/discovery.md`**](./backend/thesis/services/discovery.md): Búsqueda de literatura en Semantic Scholar.
* [**`services/exploration.md`**](./backend/thesis/services/exploration.md): Registro de idea y exploración en OpenAlex.
* [**`services/exports.md`**](./backend/thesis/services/exports.md): Exportador de borrador Markdown de Capítulos 1 al 3.
* [**`services/access.md`**](./backend/thesis/services/access.md): Guardas de pertenencia y autorización por rol.
* **Materializadores Relacionales (`services/step_materializers/`):**
  * [**`step_materializers/consistency.md`**](./backend/thesis/services/step_materializers/consistency.md): Descomposición relacional de `P01` a `P12` en tablas de consistencia y operacionalización.
  * [**`step_materializers/registry.md`**](./backend/thesis/services/step_materializers/registry.md): Despacho polimórfico en $O(1)$ de materializadores.

### 4. Capa de Adaptadores HTTP Externos (`backend/thesis/integrations/`)
* [**`integrations/alicia.md`**](./backend/thesis/integrations/alicia.md): Adaptador HTTP hacia repositorio nacional ALICIA (CONCYTEC).
* [**`integrations/openalex.md`**](./backend/thesis/integrations/openalex.md): Adaptador HTTP hacia el catálogo científico OpenAlex.
* [**`integrations/semantic_scholar.md`**](./backend/thesis/integrations/semantic_scholar.md): Adaptador HTTP hacia Semantic Scholar.
* [**`integrations/peru_articles.md`**](./backend/thesis/integrations/peru_articles.md): Filtro especializado de autores e instituciones peruanas.

### 5. Capa de Transporte REST (`backend/thesis/api/`)
* [**`api/projects.md`**](./backend/thesis/api/projects.md): Controladores HTTP con Django Ninja para proyectos, pasos y revisiones.

### 6. Capa de Migraciones Físicas (`backend/thesis/migrations/`)
* [**`migrations/0001_inicial.md`**](./backend/thesis/migrations/0001_inicial.md): Creación inicial de las 15 entidades y claves foráneas.
* [**`migrations/0002_inmutabilidad_espanol.md`**](./backend/thesis/migrations/0002_inmutabilidad_espanol.md): Triggers PL/pgSQL de inmutabilidad y tablas M2M en español.

### 7. Servidor Model Context Protocol (`mcp_server/`)
* [**`mcp_server/server.md`**](./mcp_server/server.md): Instancia `MCPServer` y herramientas de diagnóstico/catálogo.
* [**`mcp_server/project_tools.md`**](./mcp_server/project_tools.md): 14 herramientas MCP de proyectos, pasos y asesoría docente.
* [**`mcp_server/django_bridge.md`**](./mcp_server/django_bridge.md): Puente síncrono/asíncrono seguro entre el SDK MCP y Django ORM.
* [**`mcp_server/test_local.md`**](./mcp_server/test_local.md): Simulación interactiva End-to-End de los 12 pasos y revisión.
* **Prompts e Hidratación (`mcp_server/prompts/`):**
  * [**`prompts/catalog.md`**](./mcp_server/prompts/catalog.md): Registro oficial de los 15 prompts MCP.
  * [**`prompts/hydration.md`**](./mcp_server/prompts/hydration.md): Motor de inyección de contexto en vivo desde PostgreSQL.
  * [**`prompts/roles.md`**](./mcp_server/prompts/roles.md): Prompts de rol especializado (Asesor, Investigador, Revisor).
  * [**`prompts/templates.md`**](./mcp_server/prompts/templates.md): Plantillas de prompts de Capítulos 1, 2 y 3.
* **Datos de Caso y Simulación (`mcp_server/demo/`):**
  * [**`demo/case_data.md`**](./mcp_server/demo/case_data.md): Generador de payloads válidos para la simulación `P01` a `P12`.
  * [**`demo/support.md`**](./mcp_server/demo/support.md): Utilidades de emisión de credenciales e inspección SQL.

### 8. Suite de Pruebas Automatizadas (`tests/`)
* [**`tests/tests_overview.md`**](./tests/tests_overview.md): Visión general de las 32 pruebas automatizadas y estrategia de prueba.
* [**`tests/test_first_slice.md`**](./tests/test_first_slice.md): Pruebas de concurrencia OCC, triggers de inmutabilidad y `P01`.
* [**`tests/test_academic_flow.md`**](./tests/test_academic_flow.md): Pruebas de la máquina de estados y comentarios anclados.
* [**`tests/test_extended_steps.md`**](./tests/test_extended_steps.md): Pruebas del recorrido `P01`–`P12` y bloqueo de `P13`.
* [**`tests/test_chapter3.md`**](./tests/test_chapter3.md): Pruebas de la Matriz de Consistencia y Operacionalización relacional.
* [**`tests/test_discovery_peru.md`**](./tests/test_discovery_peru.md): Pruebas de ALICIA, filiación peruana y geografía.
* [**`tests/test_mcp_prompts.md`**](./tests/test_mcp_prompts.md): Pruebas de registro de prompts e hidratación dinámica.

### 9. Automatización y Verificación (`scripts/`)
* [**`scripts/verify_project.md`**](./scripts/verify_project.md): Barrera determinista Definition of Done (DoD Gate) y sus 7 auditorías.

### 10. Infraestructura y Despliegue (`infraestructura/`)
* [**`infraestructura/docker_compose.md`**](./infraestructura/docker_compose.md): Aislamiento en PostgreSQL 16 (puerto 5434), Dockerfile y compose.yaml.
