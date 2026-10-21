"""Observaciones y decisiones del asesor sobre revisiones concretas."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from thesis.models import Capitulo, ParticipanteProyecto, ComentarioRevision, EventoRevision
from thesis.services.acceso import requerir_proyecto
from thesis.services.errores import ErrorDominio
from thesis.services.pasos import PASOS_CAPITULO, obtener_capitulo_servicio


def _asesor(usuario, id_proyecto):
    proyecto = requerir_proyecto(usuario, id_proyecto)
    if not ParticipanteProyecto.objects.filter(
        project=proyecto,
        user=usuario,
        active=True,
        role=ParticipanteProyecto.Role.ASESOR,
    ).exists():
        raise ErrorDominio("NO_ENCONTRADO", "Proyecto no encontrado")
    return proyecto


def asignar_asesor_servicio(usuario, id_proyecto, correo: str) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto, solo_tesista=True)
    correo = correo.strip().lower()
    asesor = get_user_model().objects.filter(email=correo, is_active=True).first()
    if asesor is None or asesor == usuario:
        raise ErrorDominio("NO_ENCONTRADO", "Asesor activo no encontrado")
    with transaction.atomic():
        existente = ParticipanteProyecto.objects.select_for_update().filter(
            project=proyecto, role=ParticipanteProyecto.Role.ASESOR, active=True,
        ).first()
        if existente and existente.user_id != asesor.pk:
            raise ErrorDominio("CONFLICTO_VERSION", "El proyecto ya tiene un asesor activo")
        if not existente:
            participacion, creada = ParticipanteProyecto.objects.get_or_create(project=proyecto, user=asesor, defaults={
                "role": ParticipanteProyecto.Role.ASESOR,
            })
            if not creada:
                if participacion.role != ParticipanteProyecto.Role.ASESOR:
                    raise ErrorDominio("CONFLICTO_VERSION", "La persona ya tiene otro rol en el proyecto")
                participacion.active = True
                participacion.left_at = None
                participacion.save(update_fields=["active", "left_at"])
    return {"id_proyecto": str(proyecto.id), "id_asesor": asesor.pk, "correo_asesor": asesor.email}


def _capitulo_actual(proyecto, numero_capitulo: int):
    if numero_capitulo not in PASOS_CAPITULO:
        raise ErrorDominio("NO_ENCONTRADO", "Capítulo no disponible en el MVP")
    capitulo = Capitulo.objects.select_for_update().filter(project=proyecto, number=numero_capitulo).first()
    if capitulo is None:
        raise ErrorDominio("NO_ENCONTRADO", "Capítulo no encontrado")
    return capitulo


def agregar_comentario_servicio(
    usuario,
    id_proyecto,
    numero_capitulo: int,
    inicio_caracter: int,
    fin_caracter: int,
    texto_seleccionado: str,
    contenido: str,
) -> dict:
    proyecto = _asesor(usuario, id_proyecto)
    contenido = contenido.strip()
    if not contenido or len(contenido) > 5000:
        raise ErrorDominio("ERROR_VALIDACION", "La observación debe tener entre 1 y 5000 caracteres")
    with transaction.atomic():
        capitulo = _capitulo_actual(proyecto, numero_capitulo)
        if capitulo.status != Capitulo.Status.EN_REVISION:
            raise ErrorDominio("CONFLICTO_VERSION", "El capítulo no está en revisión")
        revision = capitulo.revisions.order_by("-revision_no").first()
        if (
            revision is None
            or inicio_caracter < 0
            or fin_caracter <= inicio_caracter
            or revision.content_md[inicio_caracter:fin_caracter] != texto_seleccionado
        ):
            raise ErrorDominio("ERROR_VALIDACION", "El fragmento no coincide con la revisión vigente")
        comentario = ComentarioRevision.objects.create(
            revision=revision,
            author=usuario,
            start_cp=inicio_caracter,
            end_cp=fin_caracter,
            selected_text=texto_seleccionado,
            body=contenido,
        )
    return {
        "id_comentario": comentario.pk,
        "id_revision": revision.pk,
        "estado": comentario.status,
        "texto_seleccionado": comentario.selected_text,
        "contenido": comentario.body,
    }


def listar_comentarios_servicio(usuario, id_proyecto, numero_capitulo: int) -> list[dict]:
    proyecto = requerir_proyecto(usuario, id_proyecto)
    capitulo = Capitulo.objects.filter(project=proyecto, number=numero_capitulo).first()
    if capitulo is None:
        return []
    return [
        {
            "id_comentario": comentario.pk,
            "id_revision": comentario.revision_id,
            "inicio_caracter": comentario.start_cp,
            "fin_caracter": comentario.end_cp,
            "texto_seleccionado": comentario.selected_text,
            "contenido": comentario.body,
            "estado": comentario.status,
            "id_autor": comentario.author_id,
        }
        for comentario in ComentarioRevision.objects.filter(revision__chapter=capitulo).order_by("created_at", "pk")
    ]


def resolver_comentario_servicio(usuario, id_proyecto, id_comentario: int) -> dict:
    proyecto = _asesor(usuario, id_proyecto)
    with transaction.atomic():
        comentario = ComentarioRevision.objects.select_for_update().filter(
            revision__chapter__project=proyecto,
            pk=id_comentario,
        ).first()
        if comentario is None:
            raise ErrorDominio("NO_ENCONTRADO", "Observación no encontrada")
        if comentario.status == ComentarioRevision.Status.ABIERTA:
            comentario.status = ComentarioRevision.Status.RESUELTA
            comentario.resolved_by = usuario
            comentario.resolved_at = timezone.now()
            comentario.save(update_fields=["status", "resolved_by", "resolved_at"])
    return {"id_comentario": comentario.pk, "estado": comentario.status}


def decidir_capitulo_servicio(usuario, id_proyecto, numero_capitulo: int, accion: str, motivo: str = "") -> dict:
    proyecto = _asesor(usuario, id_proyecto)
    with transaction.atomic():
        capitulo = _capitulo_actual(proyecto, numero_capitulo)
        revision = capitulo.revisions.order_by("-revision_no").first()
        if accion == EventoRevision.Action.SOLICITAR_CAMBIOS:
            if capitulo.status != Capitulo.Status.EN_REVISION or revision is None:
                raise ErrorDominio("CONFLICTO_VERSION", "El capítulo no está en revisión")
            if not ComentarioRevision.objects.filter(
                revision=revision,
                status=ComentarioRevision.Status.ABIERTA,
            ).exists():
                raise ErrorDominio("ERROR_VALIDACION", "Registra al menos una observación abierta")
            capitulo.solicitar_cambios()
        elif accion == EventoRevision.Action.APROBAR:
            if capitulo.status != Capitulo.Status.EN_REVISION or revision is None:
                raise ErrorDominio("CONFLICTO_VERSION", "El capítulo no está en revisión")
            if ComentarioRevision.objects.filter(
                revision=revision,
                status=ComentarioRevision.Status.ABIERTA,
            ).exists():
                raise ErrorDominio(
                    "OBSERVACIONES_ASESOR_SIN_RESOLVER",
                    "Resuelve las observaciones abiertas antes de aprobar",
                )
            capitulo.aprobar()
            capitulo.approved_revision = revision
            capitulo.approved_at = timezone.now()
        elif accion == EventoRevision.Action.REABRIR:
            if capitulo.status != Capitulo.Status.APROBADO or not motivo.strip():
                raise ErrorDominio("CONFLICTO_VERSION", "Reabrir exige un capítulo aprobado y un motivo")
            capitulo.reabrir()
            capitulo.approved_revision = None
            capitulo.approved_at = None
            revision = None
        else:
            raise ErrorDominio("ERROR_VALIDACION", "Decisión inválida")
        capitulo.save(update_fields=["status", "approved_revision", "approved_at", "updated_at"])
        EventoRevision.objects.create(
            chapter=capitulo,
            revision=revision,
            actor=usuario,
            action=accion,
            reason=motivo.strip(),
        )
    return obtener_capitulo_servicio(usuario, id_proyecto, numero_capitulo)


def panel_asesor(usuario) -> list[dict]:
    participaciones = (
        ParticipanteProyecto.objects.filter(
            user=usuario,
            active=True,
            role=ParticipanteProyecto.Role.ASESOR,
        )
        .select_related("project")
        .order_by("project__name")
    )
    return [
        {
            "id_proyecto": str(participacion.project_id),
            "nombre_proyecto": participacion.project.name,
            "capitulos": [
                {
                    "numero_capitulo": numero,
                    "estado": Capitulo.objects.filter(
                        project=participacion.project,
                        number=numero,
                    ).values_list("status", flat=True).first() or Capitulo.Status.BORRADOR,
                }
                for numero in PASOS_CAPITULO
            ],
        }
        for participacion in participaciones
    ]
