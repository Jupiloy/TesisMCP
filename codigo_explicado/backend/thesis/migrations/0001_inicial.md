# Explicación de Código: `backend/thesis/migrations/0001_inicial.py`

## 1. Propósito y ¿Qué hace?
Es la primera migración de base de datos de la versión reducida V1. Crea de forma limpia y consolidada las tablas relacionales para las 15 entidades del sistema, estableciendo tipos de datos, claves primarias (incluyendo UUIDs), claves foráneas con reglas de integridad (`CASCADE`, `PROTECT`), índices y restricciones de verificación (`CheckConstraint`).

## 2. Justificación Técnica y ¿Por qué lo hace?
En proyectos que evolucionan rápidamente, acumular decenas de migraciones intermedias genera lentitud en pruebas y discrepancias de esquemas. Esta migración consolida en un único archivo la creación canónica de la base de datos de la versión reducida V1, permitiendo levantar el entorno desde cero en segundos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Declara `dependencies = [('auth', '__first__'), ('contenttypes', '__first__')]`.
2. Ejecuta operaciones `migrations.CreateModel` para:
   - `Usuario` (`tesis_usuario`).
   - `TokenAccesoMcp` (`tesis_token_acceso_mcp`).
   - `Proyecto` (`tesis_proyecto`).
   - `ParticipanteProyecto` (`tesis_participante_proyecto`).
   - `PerfilInvestigacion` (`tesis_perfil_investigacion`).
   - `FilaConsistencia` (`tesis_fila_consistencia`).
   - `VariableInvestigacion` (`tesis_variable_investigacion`).
   - `VariableFilaConsistencia` (`tesis_variable_fila_consistencia`).
   - `DimensionVariable` (`tesis_dimension_variable`).
   - `Indicador` (`tesis_indicador`).
   - `Capitulo` (`tesis_capitulo`).
   - `ProgresoPaso` (`tesis_progreso_paso`).
   - `RevisionCapitulo` (`tesis_revision_capitulo`).
   - `ComentarioRevision` (`tesis_comentario_revision`).
   - `EventoRevision` (`tesis_evento_revision`).
3. Instala las restricciones de integridad `CheckConstraint` y `UniqueConstraint` en cada modelo.

## 4. Componentes y Funciones Clave
* `Migration.operations`: Lista declarativa de instrucciones DDL ejecutadas por Django sobre PostgreSQL.

## 5. Relaciones con Otras Capas y Tablas
* **Base de Datos:** Crea las 15 tablas iniciales con prefijo `tesis_` en PostgreSQL 16.
* **Migración Siguiente:** Sirve como base para [`backend/thesis/migrations/0002_inmutabilidad_espanol.py`](../../backend/thesis/migrations/0002_inmutabilidad_espanol.py).
