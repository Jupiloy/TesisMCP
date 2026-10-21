import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


MIGRACION_ANTERIOR = ("thesis", "0002_integridad_esquema")
MIGRACION_ESTADOS = ("thesis", "0003_normalizacion_estados")


def _estado_proyecto(id_proyecto) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT estado FROM tesis_proyecto WHERE id = %s",
            [id_proyecto],
        )
        return cursor.fetchone()[0]


@pytest.mark.django_db(transaction=True)
def test_migracion_estados_normaliza_y_revierte_datos_persistidos():
    """Ejecuta físicamente ambos sentidos y deja el esquema nuevamente en 0003."""
    ejecutor = MigrationExecutor(connection)
    ejecutor.migrate([MIGRACION_ANTERIOR])
    aplicaciones_anteriores = ejecutor.loader.project_state([MIGRACION_ANTERIOR]).apps
    ProyectoAnterior = aplicaciones_anteriores.get_model("thesis", "Project")
    proyecto = ProyectoAnterior.objects.create(
        name="Prueba reversible",
        title="Estado histórico",
        status="ACTIVE",
    )

    try:
        ejecutor = MigrationExecutor(connection)
        ejecutor.migrate([MIGRACION_ESTADOS])
        assert _estado_proyecto(proyecto.id) == "ACTIVO"

        ejecutor = MigrationExecutor(connection)
        ejecutor.migrate([MIGRACION_ANTERIOR])
        assert _estado_proyecto(proyecto.id) == "ACTIVE"
    finally:
        MigrationExecutor(connection).migrate([MIGRACION_ESTADOS])

