from thesis.models import Proyecto, ParticipanteProyecto
from thesis.services.errors import ErrorDominio


def requerir_proyecto(actor, project_id, *, owner_only=False) -> Proyecto:
    membership = ParticipanteProyecto.objects.select_related("project").filter(
        project_id=project_id, user=actor, active=True,
    )
    if owner_only:
        membership = membership.filter(role=ParticipanteProyecto.Role.OWNER)
    participant = membership.first()
    if participant is None:
        # No revela si existe un proyecto ajeno.
        raise ErrorDominio("NOT_FOUND", "Proyecto no encontrado")
    if participant.project.status != Proyecto.Status.ACTIVE:
        raise ErrorDominio("PROJECT_ARCHIVED", "El proyecto está archivado")
    return participant.project
