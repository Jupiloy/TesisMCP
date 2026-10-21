# Explicación de Código: `backend/thesis/services/pasos.py`

## 1. Propósito y ¿Qué hace?
Es el servicio orquestador transaccional para el guardado de pasos metodológicos (`guardar_paso_servicio`). Valida la secuencia de pasos, verifica los permisos del usuario tesista, ejecuta el contrato Pydantic correspondiente, aplica control de concurrencia optimista (`lock_version`), invoca al materializador relacional, genera una nueva revisión inmutable con hash SHA-256 y actualiza el progreso del paso.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Patrón Service Layer:** Evita acoplar la lógica transaccional ni a las vistas REST de Django Ninja ni a las herramientas del servidor MCP.
* **Control de Concurrencia Optimista (OCC):** Mediante `select_for_update()` y comparación de `lock_version`, previene colisiones y pérdidas de datos concurrentes.
* **Atomicidad Estricta (*Unit of Work*):** Todo el proceso ocurre dentro de `transaction.atomic()`; si la materialización relacional o el contrato fallan, ningún registro parcial queda guardado en PostgreSQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Comprueba pertenencia del usuario y rol `OWNER` mediante `verificar_propietario_proyecto`.
2. Verifica que el paso solicitado esté en el rango permitido (`P01` a `P12`); si no, lanza error de validación.
3. Valida el JSON recibido contra su contrato Pydantic en `contratos_pasos.CONTRATOS`.
4. Abre `with transaction.atomic():` y bloquea la fila del perfil con `PerfilInvestigacion.objects.select_for_update().get(project=project)`.
5. Valida `perfil.lock_version == version_esperada`. Si difieren, lanza `ErrorDominio("CONFLICTO_VERSION")`.
6. Si el paso no es `P01`, verifica que el paso metodológico inmediatamente anterior esté en estado `COMPLETED`.
7. Si el capítulo está en estado `APPROVED`, rechaza la modificación exigiendo que el asesor lo reabra primero.
8. Invoca `ejecutar_materializador_paso(...)` para crear/actualizar filas en tablas relacionales.
9. Inserta una nueva `RevisionCapitulo` con digest SHA-256 del contenido Markdown.
10. Actualiza `ProgresoPaso` a `COMPLETED` con el JSON validado.
11. Incrementa `profile.lock_version += 1` y persiste el perfil.

## 4. Componentes y Funciones Clave
* `guardar_paso_servicio(...)`: Orquestador transaccional completo del flujo metodológico.
* Manejo de idempotencia mediante `clave_idempotencia` UUID.

## 5. Relaciones con Otras Capas y Tablas
* **Transporte:** Consumido por el endpoint REST `PUT /projects/{id}/steps/{code}` y por la herramienta MCP `guardar_paso`.
* **Modelos Afectados:** `tesis_perfil_investigacion`, `tesis_progreso_paso`, `tesis_capitulo`, `tesis_revision_capitulo`.
* **Materializadores:** Delega en [`backend/thesis/services/materializadores_pasos/`](../../backend/thesis/services/materializadores_pasos/).
