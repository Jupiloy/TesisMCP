from thesis.models import Proyecto, ParticipanteProyecto
from thesis.services.errores import ErrorDominio


def requerir_proyecto(usuario, id_proyecto, *, solo_tesista=False) -> Proyecto:
    participaciones = ParticipanteProyecto.objects.select_related("project").filter(
        project_id=id_proyecto, user=usuario, active=True,
    )
    if solo_tesista:
        participaciones = participaciones.filter(role=ParticipanteProyecto.Role.TESISTA)
    participante = participaciones.first()
    if participante is None:
        # No revela si existe un proyecto ajeno.
        raise ErrorDominio("NO_ENCONTRADO", "Proyecto no encontrado")
    if participante.project.status != Proyecto.Status.ACTIVO:
        raise ErrorDominio("PROYECTO_ARCHIVADO", "El proyecto está archivado")
    return participante.project
