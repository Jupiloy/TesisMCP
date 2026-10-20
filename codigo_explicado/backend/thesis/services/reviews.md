# Explicación de Código: `backend/thesis/services/reviews.py`

## 1. Propósito y ¿Qué hace?
Implementa la **máquina de estados de revisión y supervisión docente** para los Capítulos 1 al 3. Gestiona el envío del capítulo por el tesista (`enviar_capitulo_servicio`), el anclaje de observaciones por posición de caracteres (`observar_fragmento_servicio`), la resolución de observaciones (`resolver_observacion_servicio`) y las decisiones formales del asesor (`decidir_capitulo_servicio`: `REQUEST_CHANGES`, `APPROVE`, `REOPEN`).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Guardas de Dominio Académico:** Un estudiante no puede enviar a revisión un capítulo cuyos pasos están incompletos. Un asesor no puede aprobar un capítulo si todavía existen comentarios sin resolver (`ADVISOR_UNRESOLVED_COMMENTS`).
* **Observaciones con Trazabilidad Exacta:** Ancla los comentarios a fragmentos seleccionados del texto (`start_cp`, `end_cp`, `selected_text`), asegurando que las observaciones docentes sean específicas y comprobables.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `enviar_capitulo_servicio`:
   - Verifica que el usuario sea `OWNER`.
   - Comprueba que todos los pasos del capítulo estén en estado `COMPLETED` en `ProgresoPaso`.
   - Transiciona el capítulo de `DRAFT` o `CHANGES_REQUESTED` a `READY`.
   - Registra un `EventoRevision` de tipo `SUBMIT`.
2. `observar_fragmento_servicio`:
   - Verifica que el usuario sea `ADVISOR`.
   - Comprueba que el rango `start_cp <= end_cp` y que `selected_text` coincida con el contenido de la revisión vigente.
   - Crea un registro en `ComentarioRevision` con estado `OPEN`.
3. `decidir_capitulo_servicio`:
   - Si la acción es `APPROVE`, comprueba que no existan observaciones `OPEN` asociadas al capítulo. Si existen, rechaza la operación con `ADVISOR_UNRESOLVED_COMMENTS`.
   - Transiciona a `APPROVED` y enlaza `approved_revision`.
   - Si la acción es `REOPEN`, solo el asesor puede reabrirlo aportando un motivo obligatorio, pasando el estado a `DRAFT`.

## 4. Componentes y Funciones Clave
* `enviar_capitulo_servicio`: Envío de entrega por parte del tesista.
* `observar_fragmento_servicio`: Anclaje de observación docente por índice de caracteres.
* `decidir_capitulo_servicio`: Aprobación, solicitud de cambios o reapertura del capítulo.
* `resolver_observacion_servicio`: Cierre de observación por parte del asesor.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Afectadas:** `tesis_capitulo`, `tesis_comentario_revision`, `tesis_evento_revision`.
* **Servidor MCP:** Expuesto mediante `enviar_capitulo`, `observar_fragmento`, `decidir_capitulo`, `resolver_observacion`.
* **Pruebas:** Verificado en profundidad por [`backend/thesis/tests/test_academic_flow.py`](../../backend/thesis/tests/test_academic_flow.py).
