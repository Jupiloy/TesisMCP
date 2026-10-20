# Explicación de Código: `backend/thesis/models/projects.py`

## 1. Propósito y ¿Qué hace?
Modela la entidad central del sistema: el `Proyecto` de tesis (`tesis_proyecto`) y sus participantes con roles autorizados en `ParticipanteProyecto` (`tesis_participante_proyecto`). Define el identificador universal UUID, título, estado de actividad y vinculación entre tesistas y asesores.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Identificadores UUIDv4:** El uso de UUID en lugar de enteros autoincrementales previene ataques de enumeración y garantiza identificadores únicos estables entre la API REST y el protocolo MCP.
* **Restricciones de Integridad por Rol:** Una tesis de pregrado en la UTP tiene típicamente un único estudiante propietario activo y un único asesor metodológico activo asignado. El modelo implementa `UniqueConstraint` condicionales a nivel de base de datos para impedir duplicidades de rol por proyecto.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `Proyecto`:
   - `id`: `UUIDField(primary_key=True, default=uuid4, editable=False)`.
   - `title`: Título de la tesis (`db_column="titulo"`).
   - `status`: Estado del proyecto (`ACTIVE` o `ARCHIVED`).
   - `created_at` y `updated_at`: Marcas de tiempo automáticas.
2. `ParticipanteProyecto`:
   - `project`: FK hacia `Proyecto`.
   - `user`: FK hacia `Usuario`.
   - `role`: Rol en el proyecto (`OWNER` para tesista, `ADVISOR` para asesor metodológico).
   - `active`: Booleano de vigencia.
   - **Restricciones físicas (`constraints`):**
     - `tesis_participante_un_propietario_activo`: `UniqueConstraint(fields=['project'], condition=Q(role='OWNER', active=True))`.
     - `tesis_participante_un_asesor_activo`: `UniqueConstraint(fields=['project'], condition=Q(role='ADVISOR', active=True))`.

## 4. Componentes y Funciones Clave
* `Proyecto`: Entidad agregada raíz de cada investigación.
* `ParticipanteProyecto`: Vinculación de control de acceso entre usuarios y proyectos con roles diferenciados.
* `RolParticipante`: Enumeración de roles (`OWNER`, `ADVISOR`).

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Físicas:** `tesis_proyecto` y `tesis_participante_proyecto`.
* **Relaciones 1:1 y 1:N:** El proyecto es propietario de [`PerfilInvestigacion`](../../backend/thesis/models/research.py), [`FilaConsistencia`](../../backend/thesis/models/research.py), [`Capitulo`](../../backend/thesis/models/chapters.py) y [`ProgresoPaso`](../../backend/thesis/models/chapters.py).
* **Control de Acceso:** Validado en cada petición por [`backend/thesis/services/access.py`](../../backend/thesis/services/access.py).
