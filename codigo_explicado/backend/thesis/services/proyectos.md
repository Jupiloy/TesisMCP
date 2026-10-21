# Explicación de Código: `backend/thesis/services/proyectos.py`

## 1. Propósito y ¿Qué hace?
Gestiona el ciclo de vida inicial de los proyectos de tesis: creación del proyecto (`crear_proyecto_servicio`), inicialización de su perfil metodológico (`PerfilInvestigacion`), asignación de roles de participantes (`OWNER` y `ADVISOR`) y consulta del estado consolidado del proyecto.

## 2. Justificación Técnica y ¿Por qué lo hace?
Asegura que un proyecto nuevo siempre nazca con su entidad agregada completa y consistente (proyecto + participante propietario + perfil de investigación con `lock_version=1`), impidiendo proyectos huérfanos o usuarios sin permisos asignados.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `crear_proyecto_servicio`:
   - Abre una transacción atómica `with transaction.atomic():`.
   - Crea la entidad `Proyecto(title=title)`.
   - Crea `ParticipanteProyecto(project=project, user=user, role='OWNER', active=True)`.
   - Crea `PerfilInvestigacion(project=project, lock_version=1)`.
   - Los capítulos y progresos no se crean de antemano: se materializan conforme el tesista avanza.
2. `asignar_asesor_servicio`:
   - Comprueba que el usuario solicitante sea `OWNER`.
   - Desactiva cualquier asesor previo activo si existiera.
   - Crea o activa a un usuario como `ADVISOR` en `ParticipanteProyecto`.

## 4. Componentes y Funciones Clave
* `crear_proyecto_servicio(user, title)`: Fábrica transaccional de nuevos proyectos.
* `asignar_asesor_servicio(id_proyecto, correo_asesor, usuario_actual)`: Asignación de asesor metodológico.
* `obtener_estado_proyecto(usuario, id_proyecto)`: Consulta del estado global y avance.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Afectadas:** `tesis_proyecto`, `tesis_participante_proyecto`, `tesis_perfil_investigacion`.
* **Consumidores:** Herramientas MCP `crear_proyecto`, `obtener_estado`, `asignar_asesor`.
