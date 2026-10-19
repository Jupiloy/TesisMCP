import hashlib

from django.db import migrations


def _nombre_seguro(base: str, origen: str) -> str:
    """Genera un identificador PostgreSQL español, único y de hasta 63 bytes."""
    sufijo = hashlib.sha1(origen.encode("utf-8")).hexdigest()[:8]
    limite_base = 63 - len(sufijo) - 1
    return f"{base[:limite_base].rstrip('_')}_{sufijo}"


def traducir_esquema_intermedio_y_restricciones(apps, schema_editor):
    conexion = schema_editor.connection
    citar = schema_editor.quote_name

    with conexion.cursor() as cursor:
        # 1. Renombrar columnas de las tablas intermedias de autorización de usuario
        cursor.execute(
            """
            ALTER TABLE tesis_usuario_grupo RENAME COLUMN user_id TO usuario_id;
            ALTER TABLE tesis_usuario_grupo RENAME COLUMN group_id TO grupo_id;
            ALTER TABLE tesis_usuario_permiso RENAME COLUMN user_id TO usuario_id;
            ALTER TABLE tesis_usuario_permiso RENAME COLUMN permission_id TO permiso_id;
            """
        )

        # 2. Renombrar restricciones (PK, FK, UNIQUE, CHECK) que no tengan prefijo tesis_
        cursor.execute(
            """
            SELECT
                tabla.relname AS tabla,
                restriccion.conname AS nombre,
                restriccion.contype AS tipo,
                COALESCE(
                    array_agg(columna.attname ORDER BY posicion.orden)
                        FILTER (WHERE columna.attname IS NOT NULL),
                    ARRAY[]::name[]
                ) AS columnas
            FROM pg_constraint AS restriccion
            JOIN pg_class AS tabla ON tabla.oid = restriccion.conrelid
            JOIN pg_namespace AS esquema ON esquema.oid = tabla.relnamespace
            LEFT JOIN LATERAL unnest(restriccion.conkey)
                WITH ORDINALITY AS posicion(numero_atributo, orden) ON TRUE
            LEFT JOIN pg_attribute AS columna
                ON columna.attrelid = tabla.oid
                AND columna.attnum = posicion.numero_atributo
            WHERE esquema.nspname = current_schema()
              AND tabla.relname LIKE 'tesis\\_%' ESCAPE '\\'
              AND restriccion.conname NOT LIKE 'tesis\\_%' ESCAPE '\\'
            GROUP BY tabla.relname, restriccion.conname, restriccion.contype
            ORDER BY tabla.relname, restriccion.conname
            """
        )
        restricciones = cursor.fetchall()

        sufijos = {
            "p": "clave_primaria",
            "u": "unico",
            "f": "clave_foranea",
            "c": "verificacion",
            "x": "exclusion",
        }
        for tabla, nombre_anterior, tipo, columnas in restricciones:
            columnas_texto = "_".join(columnas) if columnas else "regla"
            base = f"{tabla}_{columnas_texto}_{sufijos.get(tipo, 'restriccion')}"
            nombre_nuevo = _nombre_seguro(base, f"{tabla}:{nombre_anterior}")
            cursor.execute(
                f"ALTER TABLE {citar(tabla)} RENAME CONSTRAINT "
                f"{citar(nombre_anterior)} TO {citar(nombre_nuevo)}"
            )

        # 3. Renombrar índices auxiliares de FK, búsquedas y expresiones sin prefijo tesis_
        cursor.execute(
            """
            SELECT
                tabla.relname AS tabla,
                indice.relname AS nombre,
                COALESCE(
                    array_agg(columna.attname ORDER BY posicion.orden)
                        FILTER (WHERE columna.attname IS NOT NULL),
                    ARRAY[]::name[]
                ) AS columnas
            FROM pg_index AS definicion
            JOIN pg_class AS tabla ON tabla.oid = definicion.indrelid
            JOIN pg_class AS indice ON indice.oid = definicion.indexrelid
            JOIN pg_namespace AS esquema ON esquema.oid = tabla.relnamespace
            LEFT JOIN LATERAL unnest(definicion.indkey)
                WITH ORDINALITY AS posicion(numero_atributo, orden) ON TRUE
            LEFT JOIN pg_attribute AS columna
                ON columna.attrelid = tabla.oid
                AND columna.attnum = posicion.numero_atributo
            WHERE esquema.nspname = current_schema()
              AND tabla.relname LIKE 'tesis\\_%' ESCAPE '\\'
              AND indice.relname NOT LIKE 'tesis\\_%' ESCAPE '\\'
            GROUP BY tabla.relname, indice.relname
            ORDER BY tabla.relname, indice.relname
            """
        )
        indices = cursor.fetchall()

        for tabla, nombre_anterior, columnas in indices:
            columnas_texto = "_".join(columnas) if columnas else "expresion"
            base = f"{tabla}_{columnas_texto}_indice"
            nombre_nuevo = _nombre_seguro(base, f"{tabla}:{nombre_anterior}")
            cursor.execute(
                f"ALTER INDEX {citar(nombre_anterior)} RENAME TO {citar(nombre_nuevo)}"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("thesis", "0001_inicial"),
    ]

    operations = [
        migrations.RunPython(
            traducir_esquema_intermedio_y_restricciones,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION tesis_rechazar_cambio_historial()
                RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION 'El historial de revisiones y auditoría de capítulos es inmutable';
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER tesis_revision_capitulo_solo_anexar
                    BEFORE UPDATE OR DELETE ON tesis_revision_capitulo
                    FOR EACH ROW EXECUTE FUNCTION tesis_rechazar_cambio_historial();

                CREATE TRIGGER tesis_evento_revision_solo_anexar
                    BEFORE UPDATE OR DELETE ON tesis_evento_revision
                    FOR EACH ROW EXECUTE FUNCTION tesis_rechazar_cambio_historial();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS tesis_evento_revision_solo_anexar ON tesis_evento_revision;
                DROP TRIGGER IF EXISTS tesis_revision_capitulo_solo_anexar ON tesis_revision_capitulo;
                DROP FUNCTION IF EXISTS tesis_rechazar_cambio_historial();
            """,
        ),
    ]
