import django_fsm
from django.db import migrations, models
from django.db.models import Q


CAMBIOS = (
    ("tesis_proyecto", "estado", {"ACTIVE": "ACTIVO", "ARCHIVED": "ARCHIVADO"}),
    ("tesis_participante_proyecto", "rol", {"OWNER": "TESISTA", "ADVISOR": "ASESOR"}),
    ("tesis_progreso_paso", "estado", {"IN_PROGRESS": "EN_CURSO", "COMPLETED": "COMPLETADO"}),
    (
        "tesis_capitulo",
        "estado",
        {
            "DRAFT": "BORRADOR",
            "READY": "EN_REVISION",
            "CHANGES_REQUESTED": "CON_OBSERVACIONES",
            "APPROVED": "APROBADO",
        },
    ),
    ("tesis_comentario_revision", "estado", {"OPEN": "ABIERTA", "RESOLVED": "RESUELTA"}),
    (
        "tesis_evento_revision",
        "accion",
        {
            "SUBMIT": "ENVIAR",
            "REQUEST_CHANGES": "SOLICITAR_CAMBIOS",
            "APPROVE": "APROBAR",
            "REOPEN": "REABRIR",
        },
    ),
    (
        "tesis_perfil_investigacion",
        "enfoque",
        {"QUANTITATIVE": "CUANTITATIVO", "QUALITATIVE": "CUALITATIVO", "MIXED": "MIXTO"},
    ),
    (
        "tesis_variable_investigacion",
        "rol",
        {"INDEPENDENT": "INDEPENDIENTE", "DEPENDENT": "DEPENDIENTE", "OTHER": "OTRA"},
    ),
)


def _aplicar_cambios(schema_editor, cambios):
    citar = schema_editor.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE tesis_evento_revision "
            "DISABLE TRIGGER tesis_evento_revision_solo_anexar"
        )
        try:
            for tabla, columna, equivalencias in cambios:
                for anterior, nuevo in equivalencias.items():
                    cursor.execute(
                        f"UPDATE {citar(tabla)} SET {citar(columna)} = %s "
                        f"WHERE {citar(columna)} = %s",
                        [nuevo, anterior],
                    )
        finally:
            cursor.execute(
                "ALTER TABLE tesis_evento_revision "
                "ENABLE TRIGGER tesis_evento_revision_solo_anexar"
            )


def normalizar_valores(_apps, schema_editor):
    _aplicar_cambios(schema_editor, CAMBIOS)


def restaurar_valores(_apps, schema_editor):
    cambios_inversos = tuple(
        (tabla, columna, {nuevo: anterior for anterior, nuevo in equivalencias.items()})
        for tabla, columna, equivalencias in CAMBIOS
    )
    _aplicar_cambios(schema_editor, cambios_inversos)


class Migration(migrations.Migration):
    dependencies = [
        ("thesis", "0002_integridad_esquema"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="projectparticipant",
            name="tesis_participante_un_propietario_activo",
        ),
        migrations.RemoveConstraint(
            model_name="projectparticipant",
            name="tesis_participante_un_asesor_activo",
        ),
        migrations.RemoveConstraint(
            model_name="researchprofile",
            name="tesis_perfil_enfoque_valido",
        ),
        migrations.RemoveConstraint(
            model_name="researchvariable",
            name="tesis_variable_rol_valido",
        ),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("ACTIVO", "Activo"), ("ARCHIVADO", "Archivado")],
                db_column="estado",
                default="ACTIVO",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="projectparticipant",
            name="role",
            field=models.CharField(
                choices=[("TESISTA", "Tesista"), ("ASESOR", "Asesor")],
                db_column="rol",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="stepprogress",
            name="status",
            field=models.CharField(
                choices=[("EN_CURSO", "En curso"), ("COMPLETADO", "Completado")],
                db_column="estado",
                default="EN_CURSO",
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="status",
            field=django_fsm.FSMField(
                choices=[
                    ("BORRADOR", "Borrador"),
                    ("EN_REVISION", "En revisión"),
                    ("CON_OBSERVACIONES", "Con observaciones"),
                    ("APROBADO", "Aprobado"),
                ],
                db_column="estado",
                default="BORRADOR",
                max_length=18,
                protected=True,
            ),
        ),
        migrations.AlterField(
            model_name="reviewcomment",
            name="status",
            field=models.CharField(
                choices=[("ABIERTA", "Abierta"), ("RESUELTA", "Resuelta")],
                db_column="estado",
                default="ABIERTA",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="reviewevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("ENVIAR", "Enviado"),
                    ("SOLICITAR_CAMBIOS", "Observado"),
                    ("APROBAR", "Aprobado"),
                    ("REABRIR", "Reabierto"),
                ],
                db_column="accion",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="researchprofile",
            name="approach",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CUANTITATIVO", "Cuantitativo"),
                    ("CUALITATIVO", "Cualitativo"),
                    ("MIXTO", "Mixto"),
                ],
                db_column="enfoque",
                max_length=16,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="researchvariable",
            name="role",
            field=models.CharField(
                choices=[
                    ("INDEPENDIENTE", "Variable Independiente"),
                    ("DEPENDIENTE", "Variable Dependiente"),
                    ("OTRA", "Otra / Constructo"),
                ],
                db_column="rol",
                max_length=16,
            ),
        ),
        migrations.RunPython(normalizar_valores, restaurar_valores),
        migrations.AddConstraint(
            model_name="projectparticipant",
            constraint=models.UniqueConstraint(
                fields=("project",),
                condition=Q(role="TESISTA", active=True),
                name="tesis_participante_un_propietario_activo",
            ),
        ),
        migrations.AddConstraint(
            model_name="projectparticipant",
            constraint=models.UniqueConstraint(
                fields=("project",),
                condition=Q(role="ASESOR", active=True),
                name="tesis_participante_un_asesor_activo",
            ),
        ),
        migrations.AddConstraint(
            model_name="researchprofile",
            constraint=models.CheckConstraint(
                condition=Q(approach__isnull=True)
                | Q(approach__in=["CUANTITATIVO", "CUALITATIVO", "MIXTO"]),
                name="tesis_perfil_enfoque_valido",
            ),
        ),
        migrations.AddConstraint(
            model_name="researchvariable",
            constraint=models.CheckConstraint(
                condition=Q(role__in=["INDEPENDIENTE", "DEPENDIENTE", "OTRA"]),
                name="tesis_variable_rol_valido",
            ),
        ),
    ]
