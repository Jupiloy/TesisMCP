# Explicación de Código: `backend/thesis/tests/test_academic_flow.py`

## 1. Propósito y ¿Qué hace?
Verifica el **ciclo completo de interacción entre el Tesista y el Asesor**: envío de capítulo a revisión, bloqueo si faltan pasos por completar, anclaje de observaciones por posición de caracteres, bloqueo estricto de aprobación cuando existen observaciones abiertas, resolución de observaciones y aprobación final.

## 2. Justificación Técnica y ¿Por qué lo hace?
Asegura que las reglas de negocio de la supervisión docente se cumplan sin excepciones: un asesor no puede aprobar una tesis con observaciones pendientes y un tesista no puede saltarse la revisión.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Completa pasos simulados de un capítulo.
2. Intenta enviar un capítulo con pasos incompletos y verifica el rechazo.
3. Completa los pasos restantes y ejecuta `enviar_capitulo_servicio` -> estado `READY`.
4. Como asesor, registra una observación en `ComentarioRevision`.
5. Intenta aprobar con `decidir_capitulo_servicio(APPROVE)` y comprueba que falle con `ADVISOR_UNRESOLVED_COMMENTS`.
6. Marca la observación como `RESOLVED`.
7. Ejecuta nuevamente `APPROVE` y comprueba que el estado final sea `APPROVED`.

## 4. Componentes y Funciones Clave
* Pruebas de máquina de estados y transiciones de `Capitulo.status`.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** [`reviews.py`](../../backend/thesis/services/reviews.md) y [`steps.py`](../../backend/thesis/services/steps.md).
* **Tablas:** `tesis_capitulo`, `tesis_comentario_revision`, `tesis_evento_revision`.
