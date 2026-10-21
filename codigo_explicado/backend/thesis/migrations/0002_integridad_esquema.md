# Explicación de Código: `backend/thesis/migrations/0002_integridad_esquema.py`

## 1. Propósito y ¿Qué hace?
Es la segunda migración física del avance evolutivo V1. Cumple dos funciones críticas:
1. Traduce las tablas intermedias de grupos y permisos generadas por Django a nombres físicos en español: `tesis_usuario_grupo` y `tesis_usuario_permiso`.
2. Instala en el motor PostgreSQL la función PL/pgSQL `tesis_rechazar_cambio_historial()` y los disparadores (`triggers`) `tesis_revision_capitulo_solo_anexar` y `tesis_evento_revision_solo_anexar` para forzar inmutabilidad *append-only* en revisiones y bitácoras docentes.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Defensa en Profundidad:** Bloquear la edición y eliminación únicamente en la aplicación web (Python) es insuficiente ante administradores o scripts que accedan por consola SQL directa. Al implementar un disparador `BEFORE UPDATE OR DELETE` en el motor de base de datos, PostgreSQL aborta cualquier modificación retroactiva con una excepción de base de datos.
* **Esquema 100% en Español:** Normaliza el 100% de las 17 tablas del sistema bajo el prefijo `tesis_`.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Ejecuta `migrations.RunSQL` para renombrar las tablas M2M de autenticación a `tesis_usuario_grupo` y `tesis_usuario_permiso`.
2. Define la función en lenguaje PL/pgSQL:
   ```sql
   CREATE OR REPLACE FUNCTION tesis_rechazar_cambio_historial()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'Las revisiones y eventos del asesor son inmutables (append-only); no se permite modificar ni borrar';
   END;
   $$ LANGUAGE plpgsql;
   ```
3. Asocia los disparadores en PostgreSQL:
   ```sql
   CREATE TRIGGER tesis_revision_capitulo_solo_anexar
   BEFORE UPDATE OR DELETE ON tesis_revision_capitulo
   FOR EACH ROW EXECUTE FUNCTION tesis_rechazar_cambio_historial();

   CREATE TRIGGER tesis_evento_revision_solo_anexar
   BEFORE UPDATE OR DELETE ON tesis_evento_revision
   FOR EACH ROW EXECUTE FUNCTION tesis_rechazar_cambio_historial();
   ```

## 4. Componentes y Funciones Clave
* `tesis_rechazar_cambio_historial()`: Función PL/pgSQL disparadora de excepción.
* `tesis_revision_capitulo_solo_anexar`: Disparador de inmutabilidad sobre revisiones de capítulos.
* `tesis_evento_revision_solo_anexar`: Disparador de inmutabilidad sobre eventos de auditoría docente.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Afectadas:** `tesis_revision_capitulo` y `tesis_evento_revision`.
* **Pruebas Automatizadas:** Evaluado empíricamente por [`backend/thesis/tests/test_primer_corte.py`](../../backend/thesis/tests/test_primer_corte.py), que intenta forzar un `.update()` o `.delete()` y verifica que PostgreSQL lance un error operativo.
* **Puerta DoD:** Auditado en `information_schema` y `pg_catalog` por [`scripts/verify_project.py`](../../scripts/verify_project.py).
