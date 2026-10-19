# 05. Suite de Pruebas, Puerta DoD y Guía de Defensa Docente

Este documento explica cómo se verifica la calidad del código en `version_reducida_docente/`, qué valida cada archivo de pruebas y cómo responder a posibles preguntas técnicas del docente durante la presentación del avance.

---

## 1. Desglose de la Suite de Pruebas Automatizadas (`43 Tests` en `backend/thesis/tests/`)

Todas las pruebas se ejecutan contra una base de datos PostgreSQL real (`test_tesismcp_reducido_docente`) usando `pytest-django`:

| Archivo de Prueba | Qué Verifica Exactamente |
| :--- | :--- |
| [`test_health.py`](../backend/thesis/tests/test_health.py) | Verifica que el endpoint `GET /api/health` responda HTTP 200 y que el modelo personalizado `Usuario` autentique por correo electrónico. |
| [`test_first_slice.py`](../backend/thesis/tests/test_first_slice.py) | Prueba el primer corte vertical (`P01`), el rechazo de payloads inválidos, el **control de concurrencia optimista (`STALE_VERSION`)**, la creación de revisiones inmutables y verifica que los **triggers de PostgreSQL bloqueen `UPDATE` y `DELETE`** sobre `RevisionCapitulo` y `EventoRevision`. |
| [`test_discovery.py`](../backend/thesis/tests/test_discovery.py) | Prueba el registro de la idea inicial (`registrar_idea`), la búsqueda exploratoria en OpenAlex (`explorar_idea`) y la búsqueda de metadatos en Semantic Scholar con advertencias anti-alucinación. |
| [`test_discovery_peru.py`](../backend/thesis/tests/test_discovery_peru.py) | Prueba la búsqueda de tesis peruanas en ALICIA (CONCYTEC), el filtrado de artículos con filiación institucional en Perú (`PE`) y la inferencia geográfica (`geography.py`). |
| [`test_academic_flow.py`](../backend/thesis/tests/test_academic_flow.py) | Prueba el ciclo completo `TESISTA` $\leftrightarrow$ `ASESOR`: envío de capítulo a revisión, bloqueo si faltan pasos, anclaje de observaciones por posición (`start_offset`, `end_offset`), **bloqueo de aprobación cuando hay observaciones abiertas (`ADVISOR_UNRESOLVED_COMMENTS`)**, resolución de comentarios, aprobación final y bloqueo de capítulos fuera del rango 1..3. |
| [`test_extended_steps.py`](../backend/thesis/tests/test_extended_steps.py) | Prueba de punta a punta la ejecución de los **12 pasos (`P01` a `P12`)**, la exportación del borrador Markdown de los 3 capítulos y comprueba que **`P13` (Capítulo 4) sea rechazado** tanto por el catálogo como por los servicios. |
| [`test_mcp_prompts.py`](../backend/thesis/tests/test_mcp_prompts.py) | Comprueba que el servidor MCP tenga exactamente **15 prompts registrados** (12 pasos + 3 roles) y que la hidratación dinámica inyecte los datos reales del proyecto desde PostgreSQL. |
| [`extended_steps/test_chapter3.py`](../backend/thesis/tests/extended_steps/test_chapter3.py) | Prueba en profundidad la materialización relacional del Capítulo 3 (`P09` a `P12`): filas de la Matriz de Consistencia (`GENERAL` y `SPECIFIC`), variables (`VI` y `VD`), dimensiones e indicadores medibles. |

---

## 2. Cómo Funciona la Puerta de Verificación ([`scripts/verify_project.py`](../scripts/verify_project.py))

Al ejecutar:
```bash
python3 version_reducida_docente/scripts/verify_project.py
```
El script ejecuta **7 auditorías deterministas**:

1. **`manage.py check`**: Comprueba que no existan errores de configuración en Django.
2. **`makemigrations --check --dry-run`**: Comprueba que no exista ninguna diferencia entre los 15 modelos en Python y las 2 migraciones en disco.
3. **Auditoría del Esquema Físico en Español en PostgreSQL**: Se conecta directamente a `information_schema` y `pg_catalog` de PostgreSQL para verificar que existan exactamente las **17 tablas `tesis_*`**, que todas las columnas, `CheckConstraint`, `UniqueConstraint`, índices, funciones (`tesis_rechazar_cambio_historial`) y triggers estén íntegramente en español.
4. **Suite Pytest Completa**: Ejecuta los 43 tests automatizados y exige 100 % de éxito.
5. **Higiene de Repositorio**: Verifica `.gitignore` y ausencia de archivos temporales (`*.bak`, `*.tmp`, etc.).
6. **Consistencia Documentación-Código**: Verifica matemáticamente: `15` modelos, `2` migraciones, `12` pasos en capítulos `[1, 2, 3]`, `17` herramientas MCP, `15` prompts MCP y `0` enlaces Markdown rotos.
7. **Auditoría Adversaria de Contratos**: Intenta inyectar un `campo_espurio_prohibido` y una lista incompleta en `SalidaP01` para comprobar que `extra="forbid"` esté activo, y escanea los servicios para asegurar `0` datos mock en producción.

---

## 3. Guía de Preguntas y Respuestas para la Defensa ante el Docente

### Pregunta 1: *"¿Por qué su base de datos tiene 17 tablas si solo están haciendo hasta el Capítulo 3?"*
* **Respuesta técnica:**
  > "Porque no guardamos la tesis como un simple texto libre o un único JSON sin estructura. Para que el sistema garantice coherencia metodológica entre los Capítulos 1, 2 y 3, normalizamos las entidades académicas en PostgreSQL: tenemos tablas dedicadas para la Matriz de Consistencia (`tesis_fila_consistencia`), las Variables (`tesis_variable_investigacion`), su cruce (`tesis_variable_fila_consistencia`), las Dimensiones (`tesis_dimension_variable`) y los Indicadores (`tesis_indicador`), además del sistema de versionado inmutable de revisiones (`tesis_revision_capitulo`) y observaciones ancladas del asesor (`tesis_comentario_revision`)."

### Pregunta 2: *"¿Cómo evitan que el LLM invente campos JSON o se salte pasos?"*
* **Respuesta técnica:**
  > "Implementamos una capa de contratos deterministas con Pydantic V2 en `step_contracts.py` usando `ConfigDict(extra='forbid')`. Si el LLM envía un campo adicional no definido en el esquema del paso (`SalidaP01` a `SalidaP12`) o no cumple las longitudes y expresiones regulares (como el código `ODS-XX:X.X` en `P03`), el backend rechaza la transacción antes de tocar PostgreSQL."

### Pregunta 3: *"¿Qué pasa si un alumno intenta modificar un capítulo que el asesor ya aprobó, o borrar una revisión anterior?"*
* **Respuesta técnica:**
  > "Tenemos dos barreras:
  > 1. En la máquina de estados (`services/reviews.py` y `services/steps.py`), si un capítulo tiene estado `APPROVED`, cualquier intento de guardar un paso lanza la excepción de dominio `CHAPTER_APPROVED_LOCKED` (HTTP 409) hasta que el asesor lo reabra explícitamente.
  > 2. A nivel físico en PostgreSQL (`0002_inmutabilidad_espanol.py`), las tablas `tesis_revision_capitulo` y `tesis_evento_revision` tienen un trigger PL/pgSQL (`tesis_rechazar_cambio_historial`) que bloquea cualquier `UPDATE` o `DELETE` incluso si alguien entra por consola SQL."

### Pregunta 4: *"¿Cómo puedo ver funcionar los 12 pasos y la revisión del asesor ahora mismo en vivo?"*
* **Respuesta técnica:**
  > Ejecutando la simulación local de punta a punta del servidor MCP:
  ```bash
  DJANGO_DEBUG=1 .venv/bin/python version_reducida_docente/mcp_server/test_local.py
  ```
  > Ese script levanta el servidor MCP real, autentica al tesista y al asesor con tokens criptográficos SHA-256, crea un proyecto, ejecuta los pasos `P01` al `P12`, demuestra cómo el servidor bloquea el paso `P13` (Capítulo 4), registra una observación anclada del asesor en el Capítulo 3, verifica que no se pueda aprobar mientras la observación esté abierta, la resuelve y aprueba los Capítulos 1, 2 y 3.
