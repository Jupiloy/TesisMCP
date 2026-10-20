# Explicación de Código: `backend/thesis/models/chapters.py`

## 1. Propósito y ¿Qué hace?
Modela el ciclo de vida, avance de pasos y la supervisión docente del trabajo de tesis:
* `ProgresoPaso` (`tesis_progreso_paso`): Estado de ejecución de cada paso (`IN_PROGRESS` o `COMPLETED`) y su salida JSON validada.
* `Capitulo` (`tesis_capitulo`): Capítulos habilitados (restringido a 1..3 mediante `CheckConstraint`), estado de revisión (`DRAFT`, `READY`, `CHANGES_REQUESTED`, `APPROVED`) y enlace a la revisión aprobada.
* `RevisionCapitulo` (`tesis_revision_capitulo`): Historial inmutable *append-only* de entregas con contenido Markdown y resumen SHA-256.
* `ComentarioRevision` (`tesis_comentario_revision`): Observaciones ancladas a posiciones exactas de texto (`inicio_caracter`, `fin_caracter`, `texto_seleccionado`).
* `EventoRevision` (`tesis_evento_revision`): Bitácora inmutable de auditoría docente (`SUBMIT`, `REQUEST_CHANGES`, `APPROVE`, `REOPEN`).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Inmutabilidad y Trazabilidad:** Las evaluaciones académicas exigen que ni el estudiante ni el docente puedan alterar el texto de una entrega pasada ni borrar los comentarios realizados.
* **Protección contra Alucinaciones de Alcance:** La restricción `CheckConstraint(check=Q(numero__gte=1, numero__lte=3))` garantiza en el motor PostgreSQL que ningún proceso pueda crear capítulos 4 al 7 en la versión reducida V1.
* **Observaciones Ancladas:** A diferencia de comentarios genéricos de fin de documento, el modelo ancla las observaciones al fragmento exacto del manuscrito, calculando rangos positivos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `ProgresoPaso`: Almacena `salida_json` (JSONB) con los datos del contrato Pydantic.
2. `Capitulo`: Posee una clave única compuesta `(project, number)`. Gestiona las transiciones de estado de revisión.
3. `RevisionCapitulo`: Cada vez que se guarda un paso, se crea una tupla nueva con `sha256 = hashlib.sha256(content.encode()).hexdigest()`. Las tuplas previas jamás se modifican.
4. `ComentarioRevision`: Valida que `fin_caracter >= inicio_caracter` mediante `CheckConstraint`.
5. `EventoRevision`: Registra quién tomó la decisión, en qué fecha, para qué revisión y bajo qué motivo.

## 4. Componentes y Funciones Clave
* `Capitulo`: Modelo central de estado del capítulo (1..3).
* `EstadoCapitulo`: Estados admitidos (`DRAFT`, `READY`, `CHANGES_REQUESTED`, `APPROVED`).
* `RevisionCapitulo`: Historial *append-only* de documentos Markdown.
* `ComentarioRevision`: Observación anclada por rango de caracteres.
* `TipoEventoRevision`: Acciones docentes auditadas.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Físicas en PostgreSQL:** `tesis_progreso_paso`, `tesis_capitulo`, `tesis_revision_capitulo`, `tesis_comentario_revision`, `tesis_evento_revision`.
* **Triggers PL/pgSQL:** `tesis_revision_capitulo` y `tesis_evento_revision` están protegidas contra `UPDATE` y `DELETE` por los disparadores instalados en [`0002_inmutabilidad_espanol.py`](../../backend/thesis/migrations/0002_inmutabilidad_espanol.py).
* **Máquina de Estados:** Operado por [`backend/thesis/services/reviews.py`](../../backend/thesis/services/reviews.py).
