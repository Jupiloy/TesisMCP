# Guía Pedagógica y Mapa del Código Fuente (`V1/codigo_explicado/`)

Bienvenido a la documentación explicativa **archivo por archivo** del **avance evolutivo V1 de TesisMCP (Capítulos 1 al 3)**.

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
  * [**`config/api.md`**](./backend/config/api.md): Instancia raíz de `NinjaAPI`, errores públicos y enrutador REST.
  * [**`config/urls.md`**](./backend/config/urls.md): Enrutamiento URL raíz de endpoints web y administrativos.
* **Dominio Metodológico Base (`backend/thesis/`):**
  * [**`thesis/admin.md`**](./backend/thesis/admin.md): Panel de administración con protección *append-only* en revisiones.
  * [**`thesis/catalogo_pasos.md`**](./backend/thesis/catalogo_pasos.md): Catálogo canónico de los 12 pasos metodológicos (`P01`–`P12`).
  * [**`thesis/management/emitir_token_mcp.md`**](./backend/thesis/management/emitir_token_mcp.md): Comando CLI para emitir tokens opacos SHA-256.

### 2. Capa de Persistencia Relacional (`backend/thesis/models/`)
* [**`models/accounts.md`**](./backend/thesis/models/accounts.md): Autenticación de `Usuario` y `TokenAccesoMcp` (hash SHA-256).
* [**`models/projects.md`**](./backend/thesis/models/projects.md): `Proyecto` y `ParticipanteProyecto` (roles `OWNER` y `ADVISOR`).
* [**`models/research.md`**](./backend/thesis/models/research.md): `PerfilInvestigacion` (con `lock_version`), `FilaConsistencia`, variables, dimensiones e indicadores.
* [**`models/chapters.md`**](./backend/thesis/models/chapters.md): `Capitulo` (1..3), `RevisionCapitulo` (inmutable), `ComentarioRevision` (anclado) y `EventoRevision`.
* [**`models/mapeo_modelos.md`**](./backend/thesis/models/mapeo_modelos.md): Mapeo de `COLUMNAS_FISICAS` y alias públicos de las 17 tablas `tesis_*`.

### 3. Capa de Servicios de Dominio (`backend/thesis/services/`)
* [**`services/contratos_pasos.md`**](./backend/thesis/services/contratos_pasos.md): Contratos Pydantic V2 (`SalidaP01` a `SalidaP12`) con `extra="forbid"`.
* [**`services/pasos.md`**](./backend/thesis/services/pasos.md): Orquestación transaccional `guardar_paso_servicio` con control OCC (`lock_version`).
* [**`services/revisiones.md`**](./backend/thesis/services/revisiones.md): Máquina de estados de revisión del asesor y observaciones ancladas.
* [**`services/proyectos.md`**](./backend/thesis/services/proyectos.md): Inicialización atómica de proyecto y perfil.
* [**`services/autenticacion_mcp.md`**](./backend/thesis/services/autenticacion_mcp.md): Emisión y validación segura de tokens opacos.
* [**`services/descubrimiento_peru.md`**](./backend/thesis/services/descubrimiento_peru.md): Búsqueda en repositorio ALICIA CONCYTEC y filiación peruana.
* [**`services/geografia.md`**](./backend/thesis/services/geografia.md): Inferencia determinista de ámbito geográfico de investigación.
* [**`services/descubrimiento.md`**](./backend/thesis/services/descubrimiento.md): Búsqueda de literatura en Semantic Scholar.
* [**`services/exploracion.md`**](./backend/thesis/services/exploracion.md): Registro de idea y exploración en OpenAlex.
* [**`services/exportaciones.md`**](./backend/thesis/services/exportaciones.md): Exportador de borrador Markdown de Capítulos 1 al 3.
* [**`services/acceso.md`**](./backend/thesis/services/acceso.md): Guardas de pertenencia y autorización por rol.
* **Materializadores Relacionales (`services/materializadores_pasos/`):**
  * [**`materializadores_pasos/consistencia.md`**](./backend/thesis/services/materializadores_pasos/consistencia.md): Descomposición relacional de `P01` a `P12` en tablas de consistencia y operacionalización.
  * [**`materializadores_pasos/registro.md`**](./backend/thesis/services/materializadores_pasos/registro.md): Despacho polimórfico en $O(1)$ de materializadores.

### 4. Capa de Adaptadores HTTP Externos (`backend/thesis/integrations/`)
* [**`integrations/alicia.md`**](./backend/thesis/integrations/alicia.md): Adaptador HTTP hacia repositorio nacional ALICIA (CONCYTEC).
* [**`integrations/openalex.md`**](./backend/thesis/integrations/openalex.md): Adaptador HTTP hacia el catálogo científico OpenAlex.
* [**`integrations/semantic_scholar.md`**](./backend/thesis/integrations/semantic_scholar.md): Adaptador HTTP hacia Semantic Scholar.
* [**`integrations/articulos_peru.md`**](./backend/thesis/integrations/articulos_peru.md): Filtro especializado de autores e instituciones peruanas.

### 5. Capa de Transporte REST (`backend/thesis/api/`)
* [**`api/proyectos.md`**](./backend/thesis/api/proyectos.md): Controladores HTTP con Django Ninja para proyectos, pasos y revisiones.

### 6. Capa de Migraciones Físicas (`backend/thesis/migrations/`)
* [**`migrations/0001_inicial.md`**](./backend/thesis/migrations/0001_inicial.md): Creación inicial de las 15 entidades y claves foráneas.
* [**`migrations/0002_integridad_esquema.md`**](./backend/thesis/migrations/0002_integridad_esquema.md): Triggers PL/pgSQL de inmutabilidad y tablas M2M en español.

### 7. Servidor Model Context Protocol (`mcp_server/`)
* [**`mcp_server/server.md`**](./mcp_server/server.md): Instancia `MCPServer` y herramientas de diagnóstico/catálogo.
* [**`mcp_server/herramientas_proyecto.md`**](./mcp_server/herramientas_proyecto.md): 14 herramientas MCP de proyectos, pasos y asesoría docente.
* [**`mcp_server/puente_django.md`**](./mcp_server/puente_django.md): Puente síncrono/asíncrono seguro entre el SDK MCP y Django ORM.
* [**`mcp_server/prueba_local.md`**](./mcp_server/prueba_local.md): Simulación interactiva de punta a punta de los 12 pasos y revisión.
* **Prompts e Hidratación (`mcp_server/prompts/`):**
  * [**`prompts/catalogo.md`**](./mcp_server/prompts/catalogo.md): Registro oficial de los 15 prompts MCP.
  * [**`prompts/hidratacion.md`**](./mcp_server/prompts/hidratacion.md): Motor de inyección de contexto en vivo desde PostgreSQL.
  * [**`prompts/roles.md`**](./mcp_server/prompts/roles.md): Prompts de rol especializado (Asesor, Investigador, Revisor).
  * [**`prompts/plantillas.md`**](./mcp_server/prompts/plantillas.md): Plantillas de prompts de Capítulos 1, 2 y 3.
* **Datos de Caso y Simulación (`mcp_server/demostracion/`):**
  * [**`demostracion/datos_caso.md`**](./mcp_server/demostracion/datos_caso.md): Generador de cargas válidas para la simulación `P01` a `P12`.
  * [**`demostracion/soporte.md`**](./mcp_server/demostracion/soporte.md): Utilidades de emisión de credenciales e inspección SQL.

### 8. Suite de Pruebas Automatizadas (`tests/`)
* [**`tests/tests_overview.md`**](./tests/tests_overview.md): Visión general de las 34 pruebas automatizadas y estrategia de prueba.
* [**`tests/test_primer_corte.md`**](./tests/test_primer_corte.md): Pruebas de concurrencia OCC, triggers de inmutabilidad y `P01`.
* [**`tests/test_flujo_academico.md`**](./tests/test_flujo_academico.md): Pruebas de la máquina de estados y comentarios anclados.
* [**`tests/test_pasos_ampliados.md`**](./tests/test_pasos_ampliados.md): Pruebas del recorrido `P01`–`P12` y bloqueo de `P13`.
* [**`tests/test_capitulo3.md`**](./tests/test_capitulo3.md): Pruebas de la Matriz de Consistencia y Operacionalización relacional.
* [**`tests/test_descubrimiento_peru.md`**](./tests/test_descubrimiento_peru.md): Pruebas de ALICIA, filiación peruana y geografía.
* [**`tests/test_prompts_mcp.md`**](./tests/test_prompts_mcp.md): Pruebas de registro de prompts e hidratación dinámica.

### 9. Automatización y Verificación (`scripts/`)
* [**`scripts/verify_project.md`**](./scripts/verify_project.md): Barrera determinista Definition of Done (DoD Gate) y sus 7 auditorías.

### 10. Infraestructura y Despliegue (`infraestructura/`)
* [**`infraestructura/docker_compose.md`**](./infraestructura/docker_compose.md): Aislamiento en PostgreSQL 16 (puerto 5434), Dockerfile y compose.yaml.
