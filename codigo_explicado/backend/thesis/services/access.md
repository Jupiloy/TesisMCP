# Explicación de Código: `backend/thesis/services/access.py`

## 1. Propósito y ¿Qué hace?
Centraliza las **guardas de autorización y control de acceso** para los proyectos de tesis. Verifica que un usuario pertenezca al proyecto antes de consultar datos, y valida si su rol es `OWNER` (estudiante tesista) o `ADVISOR` (asesor docente).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Seguridad Multi-Inquilino:** Evita fugas de datos (*Data Leaks*) impidiendo que un estudiante pueda ver o alterar la tesis de otro alumno.
* **Separación de Responsabilidades:** Solo el `OWNER` puede guardar pasos o enviar capítulos; solo el `ADVISOR` puede aprobar, solicitar cambios o reabrir capítulos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `verificar_participante_proyecto(user, project)`: Busca en `ParticipanteProyecto` un registro activo para la tupla `(user, project)`. Si no existe, lanza `ErrorDominio("FORBIDDEN", 403)`.
2. `verificar_propietario_proyecto(user, project)`: Exige que el rol sea estrictamente `OWNER`.
3. `verificar_asesor_proyecto(user, project)`: Exige que el rol sea estrictamente `ADVISOR`.

## 4. Componentes y Funciones Clave
* `verificar_participante_proyecto(...)`: Guarda de pertenencia.
* `verificar_propietario_proyecto(...)`: Guarda exclusiva de tesista.
* `verificar_asesor_proyecto(...)`: Guarda exclusiva de asesor.

## 5. Relaciones con Otras Capas y Tablas
* **Modelo:** Consulta [`ParticipanteProyecto`](../../backend/thesis/models/projects.py) (`tesis_participante_proyecto`).
* **Invocadores:** Llamado en la primera línea de cada servicio en `steps.py`, `reviews.py`, `projects.py` y `exports.py`.
