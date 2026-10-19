from django.db import transaction
from django.db.models import F
from django.utils import timezone

from thesis.models import Proyecto, ParticipanteProyecto, PerfilInvestigacion
from thesis.services.access import requerir_proyecto
from thesis.services.errors import ErrorDominio


def _limpiar_texto(value: str, name: str, max_length: int) -> str:
    cleaned = value.strip()
    if not cleaned or len(cleaned) > max_length:
        raise ErrorDominio("VALIDATION_ERROR", f"{name} debe tener entre 1 y {max_length} caracteres")
    return cleaned


@transaction.atomic
def crear_proyecto_servicio(actor, name: str, title: str | None = None) -> Proyecto:
    project = Proyecto.objects.create(
        name=_limpiar_texto(name, "name", 160),
        title=_limpiar_texto(title, "title", 300) if title else "Título por definir",
    )
    ParticipanteProyecto.objects.create(project=project, user=actor, role=ParticipanteProyecto.Role.OWNER)
    PerfilInvestigacion.objects.create(project=project)
    return project


def obtener_estado_proyecto(actor, project_id) -> dict:
    project = requerir_proyecto(actor, project_id)
    profile = project.profile
    consistency_rows = [
        {
            "ordinal": row.ordinal,
            "objective_text": row.objective_text,
            "question_text": row.question_text,
            "hypothesis_text": row.hypothesis_text,
        }
        for row in project.consistency_rows.order_by("ordinal")
    ]
    variables = [
        {
            "ordinal": var.ordinal,
            "role": var.role,
            "name": var.name,
            "conceptual_definition": var.conceptual_definition,
            "operational_definition": var.operational_definition,
            "dimensions": [
                {
                    "ordinal": dim.ordinal,
                    "name": dim.name,
                    "indicators": [
                        {
                            "ordinal": ind.ordinal,
                            "name": ind.name,
                            "measurement_scale": ind.measurement_scale,
                        }
                        for ind in dim.indicators.order_by("ordinal")
                    ],
                }
                for dim in var.dimensions.order_by("ordinal")
            ],
        }
        for var in project.variables.order_by("ordinal")
    ]
    return {
        "project_id": str(project.id),
        "name": project.name,
        "title": project.title,
        "status": project.status,
        "idea_provisional": profile.topic,
        "problem_statement": profile.problem_statement,
        "ods_code": profile.ods_code,
        "unit_of_analysis": profile.unit_of_analysis,
        "place": profile.place,
        "period_text": profile.period_text,
        "approach": profile.approach,
        "consistency_matrix": consistency_rows,
        "variables": variables,
        "state_version": profile.lock_version,
    }


@transaction.atomic
def registrar_idea_servicio(actor, project_id, description: str, expected_version: int) -> dict:
    project = requerir_proyecto(actor, project_id, owner_only=True)
    idea = _limpiar_texto(description, "description", 2000)
    updated = PerfilInvestigacion.objects.filter(
        project=project, lock_version=expected_version,
    ).update(topic=idea, lock_version=F("lock_version") + 1, updated_at=timezone.now())
    if not updated:
        raise ErrorDominio("VERSION_CONFLICT", "La idea cambió; consulta el estado actual antes de guardar")
    return obtener_estado_proyecto(actor, project.id)
