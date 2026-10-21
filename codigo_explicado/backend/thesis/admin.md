# Explicación de Código: `backend/thesis/admin.py`

## 1. Propósito y ¿Qué hace?
Configura y personaliza el panel administrativo de Django para los 15 modelos del sistema. Implementa protecciones de seguridad en la interfaz gráfica para impedir que administradores puedan editar o borrar revisiones de capítulos (`RevisionCapitulo`) y registros de eventos (`EventoRevision`), garantizando el principio de auditoría inmutable *append-only*.

## 2. Justificación Técnica y ¿Por qué lo hace?
En una plataforma académica donde se evalúan tesis universitarias, las actas de revisión, comentarios y entregas constituyen documentos con validez institucional. Permitir que un administrador altere retroactivamente el texto de una revisión o elimine una desaprobación comprometería la integridad del sistema. El panel admin refleja en la interfaz gráfica la misma restricción que imponen los disparadores en PostgreSQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Sobrescribe `has_delete_permission(self, request, obj=None)` retornando `False` en `RevisionCapituloAdmin` y `EventoRevisionAdmin`.
2. Define `has_change_permission(self, request, obj=None)` retornando `False` para bloquear el formulario de edición de revisiones ya creadas.
3. Establece todos los campos de `RevisionCapitulo` y `EventoRevision` como `readonly_fields`.
4. Configura filtros de búsqueda, filtros laterales por estado y visualización de columnas clave en `ProyectoAdmin`, `UsuarioAdmin`, `PerfilInvestigacionAdmin` y `FilaConsistenciaAdmin`.

## 4. Componentes y Funciones Clave
* `RevisionCapituloAdmin`: Configuración administrativa con permisos de solo lectura y bloqueo de eliminación.
* `EventoRevisionAdmin`: Configuración administrativa con permisos inmutables para la bitácora de eventos del asesor.
* `UsuarioAdmin`: Administración personalizada para el modelo de usuario con autenticación por email.
* `FilaConsistenciaInline`: Vista embebida de objetivos, preguntas e hipótesis dentro del panel de perfil.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos:** Protege [`RevisionCapitulo`](../../backend/thesis/models/chapters.py) (`tesis_revision_capitulo`) y [`EventoRevision`](../../backend/thesis/models/chapters.py) (`tesis_evento_revision`).
* **Base de Datos:** Se alinea con los triggers instalados en [`0002_integridad_esquema.py`](../../backend/thesis/migrations/0002_integridad_esquema.py).
