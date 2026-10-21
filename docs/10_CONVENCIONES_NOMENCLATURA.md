# 10. Convenciones de Nomenclatura en Español

## 1. Regla permanente

Todo identificador, contrato y concepto controlado por TesisMCP se expresa en español. La regla comprende rutas HTTP, parámetros de ruta y consulta, cargas y respuestas JSON, nombres de esquemas propios, servicios, variables, funciones, errores, estados públicos, herramientas MCP, pruebas y documentación.

No se traducen nombres impuestos por Python, Django, Django Ninja, Pydantic, PostgreSQL, HTTP ni dependencias externas. Son ejemplos válidos `__init__.py`, `settings.py`, `request.user`, `model_validate`, `GET`, `POST`, `UUID`, `JSON`, `DJANGO_SETTINGS_MODULE` y las claves originales que se envían a una API externa.

## 2. Inventario verificado y clasificación

El inventario se obtuvo mediante búsqueda textual sobre `backend/`, `mcp_server/`, `tests/`, migraciones y documentación, seguida de inspección de los archivos que definen cada contrato.

| Clasificación | Hallazgos comprobados antes de la normalización | Ubicación comprobada | Decisión |
| :--- | :--- | :--- | :--- |
| 1. Dominio controlado por TesisMCP | Variables y parámetros `actor`, `project_id`, `step_code`, `chapter_no`, `expected_version`, `idempotency_key`, `query`, `limit`; módulos propios `projects`, `steps`, `reviews`, `discovery`, `project_tools`; estados derivados `AVAILABLE`, `BLOCKED`; acción `SAVE`; conceptos `PENDING_EVIDENCE` y `METADATA_ONLY`. | `backend/thesis/services/`, `backend/thesis/integrations/`, `mcp_server/` | Traducidos a nombres y valores españoles en servicios, MCP y contratos normalizados. |
| 2. Contrato público existente | Rutas `/session/me`, `/methodology/catalog`, `/projects`; campos `name`, `title`, `content_md`, `output_data`, `state_version`, `allowed_actions`; errores con `code`, `message`, `detail` y `VERSION_CONFLICT`. | `backend/config/api.py`, `backend/thesis/api/proyectos.py`, pruebas y documentos 01, 03, 05, 07, 08 y 09 | Migrados al contrato canónico español. No se mantienen rutas inglesas duplicadas porque el frontend inspeccionado todavía no realiza llamadas HTTP. |
| 3. Convención externa o de framework | `request.user`, `model_validate`, `model_dump`, `GET`, `POST`, `PUT`, `UUID`, `JSON`, `on_delete`, `update_fields`, variables de entorno y claves crudas de OpenAlex, Semantic Scholar y ALICIA. | Configuración Django/Ninja, modelos, Pydantic e integraciones | Se conservan cuando la firma o el protocolo externo las exige. Las respuestas normalizadas propias sí usan español. |
| 4. Compatibilidad histórica de migraciones o base de datos | Clases y atributos ORM históricos `Project`, `Chapter`, `status`, `lock_version`, `content_md`, entre otros, fijados en `0001_inicial`; valores persistidos `ACTIVE`, `COMPLETED`, `DRAFT`, `OPEN`, `APPROVE` y relacionados. | `backend/thesis/models/`, `backend/thesis/migrations/0001_inicial.py` y `0002_integridad_esquema.py` | Las clases y atributos históricos se conservan para no romper el grafo de migraciones. Los valores persistidos se normalizan con `0003_normalizacion_estados`, migración explícita y reversible. |

## 3. Tabla antes → después

| Antes | Después canónico |
| :--- | :--- |
| `/api/v1/session/me` | `/api/v1/sesion/actual` |
| `/health/` | `/salud/` |
| `/api/v1/methodology/catalog` | `/api/v1/metodologia/catalogo` |
| `/api/v1/projects/{project_id}` | `/api/v1/proyectos/{id_proyecto}` |
| `api/projects.py` | `api/proyectos.py` |
| `services/projects.py`, `steps.py`, `reviews.py` | `services/proyectos.py`, `pasos.py`, `revisiones.py` |
| `project_tools.py`, `django_bridge.py` | `herramientas_proyecto.py`, `puente_django.py` |
| `test_local.py`, `demo/` | `prueba_local.py`, `demostracion/` |
| `steps/{step_code}` | `pasos/{codigo_paso}` |
| `chapters/{chapter_no}/submit` | `capitulos/{numero_capitulo}/enviar` |
| `content_md` | `contenido_md` |
| `output_data` | `datos_salida` |
| `expected_version` | `version_esperada` |
| `idempotency_key` | `clave_idempotencia` |
| `state_version` | `version_estado` |
| `allowed_actions: ["SAVE"]` | `acciones_permitidas: ["GUARDAR"]` |
| `VERSION_CONFLICT` | `CONFLICTO_VERSION` |
| `code`, `message`, `detail` | `codigo`, `mensaje`, `detalle` |
| `ACTIVE`, `ARCHIVED` | `ACTIVO`, `ARCHIVADO` |
| `COMPLETED`, `AVAILABLE`, `BLOCKED` | `COMPLETADO`, `DISPONIBLE`, `BLOQUEADO` |
| `DRAFT`, `READY`, `CHANGES_REQUESTED`, `APPROVED` | `BORRADOR`, `EN_REVISION`, `CON_OBSERVACIONES`, `APROBADO` |
| `OPEN`, `RESOLVED` | `ABIERTA`, `RESUELTA` |
| `SUBMIT`, `REQUEST_CHANGES`, `APPROVE`, `REOPEN` | `ENVIAR`, `SOLICITAR_CAMBIOS`, `APROBAR`, `REABRIR` |

## 4. Contrato HTTP canónico

```text
GET  /api/v1/sesion/actual
GET  /api/v1/metodologia/catalogo
GET  /api/v1/proyectos
POST /api/v1/proyectos
GET  /api/v1/proyectos/{id_proyecto}
PUT  /api/v1/proyectos/{id_proyecto}/pasos/{codigo_paso}
GET  /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}
POST /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/enviar
GET  /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/comentarios
POST /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/comentarios
GET  /api/v1/asesor/panel
```

La carga de guardado de paso es:

```json
{
  "contenido_md": "...",
  "datos_salida": {},
  "version_esperada": 0,
  "clave_idempotencia": "uuid"
}
```

Los errores públicos de HTTP y las cargas JSON incluidas en errores MCP siempre tienen la forma:

```json
{
  "codigo": "CONFLICTO_VERSION",
  "mensaje": "El perfil cambió; consulta la versión actual",
  "detalle": "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual"
}
```

## 5. Compatibilidad temporal pendiente de retirar

No quedan rutas ni campos HTTP ingleses como alias transitorios: el prototipo frontend inspeccionado aún no contiene cliente HTTP ni llamadas `fetch`, por lo que conservarlos no evita una rotura real y sí duplicaría el contrato.

La única compatibilidad temporal es interna: clases y atributos ORM ingleses definidos por la migración inicial. Se retirarán únicamente cuando exista una migración de estado que renombre los modelos y campos sin perder datos, se regenere una base limpia, se actualicen Admin, servicios, MCP y pruebas, y tanto la puerta `V1/scripts/verify_project.py` como la puerta global retornen código 0. Hasta entonces, no deben exponerse en HTTP ni MCP.

## 6. Reglas para nombres futuros

1. Todo recurso, función, variable, esquema, campo JSON, error y estado nuevo se nombra en español desde su primer cambio.
2. Los nombres de proveedor o estándar se conservan como nombres propios: `OpenAlex`, `Semantic Scholar`, `DOI`, `PDF`, `DOCX`, `MCP`, `HTTP`, `UUID` y `JSON`.
3. Una clave externa se conserva solo dentro del adaptador que habla con el proveedor; el adaptador devuelve una representación normalizada en español.
4. Ningún alias de compatibilidad se añade sin consumidor comprobado, fecha o condición de retiro y pruebas de ambos contratos.
5. Los cambios de valores persistidos requieren migración explícita reversible; nunca se editan migraciones históricas ni datos mediante reemplazos mecánicos.
6. Las pruebas deben rechazar la reaparición de rutas, claves, errores o estados públicos ingleses.
