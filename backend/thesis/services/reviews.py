"""Observaciones y decisiones del asesor sobre revisiones concretas."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from thesis.models import Capitulo, ParticipanteProyecto, ComentarioRevision, EventoRevision
from thesis.services.access import requerir_proyecto
from thesis.services.errors import ErrorDominio
from thesis.services.steps import PASOS_CAPITULO, obtener_capitulo_servicio


def _asesor(actor, project_id):
    project = requerir_proyecto(actor, project_id)
    if not ParticipanteProyecto.objects.filter(project=project, user=actor, active=True,
                                             role=ParticipanteProyecto.Role.ADVISOR).exists():
        raise ErrorDominio("NOT_FOUND", "Proyecto no encontrado")
    return project


def asignar_asesor_servicio(actor, project_id, email: str) -> dict:
    project = requerir_proyecto(actor, project_id, owner_only=True)
    email = email.strip().lower()
    advisor = get_user_model().objects.filter(email=email, is_active=True).first()
    if advisor is None or advisor == actor:
        raise ErrorDominio("NOT_FOUND", "Asesor activo no encontrado")
    with transaction.atomic():
        existing = ParticipanteProyecto.objects.select_for_update().filter(
            project=project, role=ParticipanteProyecto.Role.ADVISOR, active=True,
        ).first()
        if existing and existing.user_id != advisor.pk:
            raise ErrorDominio("VERSION_CONFLICT", "El proyecto ya tiene un asesor activo")
        if not existing:
            membership, created = ParticipanteProyecto.objects.get_or_create(project=project, user=advisor, defaults={
                "role": ParticipanteProyecto.Role.ADVISOR,
            })
            if not created:
                if membership.role != ParticipanteProyecto.Role.ADVISOR:
                    raise ErrorDominio("VERSION_CONFLICT", "La persona ya tiene otro rol en el proyecto")
                membership.active = True
                membership.left_at = None
                membership.save(update_fields=["active", "left_at"])
    return {"project_id": str(project.id), "advisor_id": advisor.pk, "advisor_email": advisor.email}


def _capitulo_actual(project, chapter_no: int):
    if chapter_no not in PASOS_CAPITULO:
        raise ErrorDominio("NOT_FOUND", "Capítulo no disponible en el MVP")
    chapter = Capitulo.objects.select_for_update().filter(project=project, number=chapter_no).first()
    if chapter is None:
        raise ErrorDominio("NOT_FOUND", "Capítulo no encontrado")
    return chapter


def agregar_comentario_servicio(actor, project_id, chapter_no: int, start_cp: int, end_cp: int,
                selected_text: str, body: str) -> dict:
    project = _asesor(actor, project_id)
    body = body.strip()
    if not body or len(body) > 5000:
        raise ErrorDominio("VALIDATION_ERROR", "La observación debe tener entre 1 y 5000 caracteres")
    with transaction.atomic():
        chapter = _capitulo_actual(project, chapter_no)
        if chapter.status != Capitulo.Status.READY:
            raise ErrorDominio("VERSION_CONFLICT", "El capítulo no está en revisión")
        revision = chapter.revisions.order_by("-revision_no").first()
        if revision is None or start_cp < 0 or end_cp <= start_cp or revision.content_md[start_cp:end_cp] != selected_text:
            raise ErrorDominio("VALIDATION_ERROR", "El fragmento no coincide con la revisión vigente")
        comment = ComentarioRevision.objects.create(revision=revision, author=actor, start_cp=start_cp,
                                               end_cp=end_cp, selected_text=selected_text, body=body)
    return {"comment_id": comment.pk, "revision_id": revision.pk, "status": comment.status,
            "selected_text": comment.selected_text, "body": comment.body}


def listar_comentarios_servicio(actor, project_id, chapter_no: int) -> list[dict]:
    project = requerir_proyecto(actor, project_id)
    chapter = Capitulo.objects.filter(project=project, number=chapter_no).first()
    if chapter is None:
        return []
    return [{"comment_id": item.pk, "revision_id": item.revision_id,
             "start_cp": item.start_cp, "end_cp": item.end_cp, "selected_text": item.selected_text,
             "body": item.body, "status": item.status, "author_id": item.author_id}
            for item in ComentarioRevision.objects.filter(revision__chapter=chapter).order_by("created_at", "pk")]


def resolver_comentario_servicio(actor, project_id, comment_id: int) -> dict:
    project = _asesor(actor, project_id)
    with transaction.atomic():
        item = ComentarioRevision.objects.select_for_update().filter(revision__chapter__project=project, pk=comment_id).first()
        if item is None:
            raise ErrorDominio("NOT_FOUND", "Observación no encontrada")
        if item.status == ComentarioRevision.Status.OPEN:
            item.status = ComentarioRevision.Status.RESOLVED
            item.resolved_by = actor
            item.resolved_at = timezone.now()
            item.save(update_fields=["status", "resolved_by", "resolved_at"])
    return {"comment_id": item.pk, "status": item.status}


def decidir_capitulo_servicio(actor, project_id, chapter_no: int, action: str, reason: str = "") -> dict:
    project = _asesor(actor, project_id)
    with transaction.atomic():
        chapter = _capitulo_actual(project, chapter_no)
        revision = chapter.revisions.order_by("-revision_no").first()
        if action == EventoRevision.Action.REQUEST_CHANGES:
            if chapter.status != Capitulo.Status.READY or revision is None:
                raise ErrorDominio("VERSION_CONFLICT", "El capítulo no está en revisión")
            if not ComentarioRevision.objects.filter(revision=revision, status=ComentarioRevision.Status.OPEN).exists():
                raise ErrorDominio("VALIDATION_ERROR", "Registra al menos una observación abierta")
            chapter.request_changes()
        elif action == EventoRevision.Action.APPROVE:
            if chapter.status != Capitulo.Status.READY or revision is None:
                raise ErrorDominio("VERSION_CONFLICT", "El capítulo no está en revisión")
            if ComentarioRevision.objects.filter(revision=revision, status=ComentarioRevision.Status.OPEN).exists():
                raise ErrorDominio("ADVISOR_UNRESOLVED_COMMENTS", "Resuelve las observaciones abiertas antes de aprobar")
            chapter.approve()
            chapter.approved_revision = revision
            chapter.approved_at = timezone.now()
        elif action == EventoRevision.Action.REOPEN:
            if chapter.status != Capitulo.Status.APPROVED or not reason.strip():
                raise ErrorDominio("VERSION_CONFLICT", "Reabrir exige un capítulo aprobado y un motivo")
            chapter.reopen()
            chapter.approved_revision = None
            chapter.approved_at = None
            revision = None
        else:
            raise ErrorDominio("VALIDATION_ERROR", "Decisión inválida")
        chapter.save(update_fields=["status", "approved_revision", "approved_at", "updated_at"])
        EventoRevision.objects.create(chapter=chapter, revision=revision, actor=actor, action=action, reason=reason.strip())
    return obtener_capitulo_servicio(actor, project_id, chapter_no)


def panel_asesor(actor) -> list[dict]:
    projects = (ParticipanteProyecto.objects.filter(user=actor, active=True, role=ParticipanteProyecto.Role.ADVISOR)
                .select_related("project").order_by("project__name"))
    return [{"project_id": str(row.project_id), "project_name": row.project.name,
             "chapters": [{"chapter_no": no, "status": Capitulo.objects.filter(
                 project=row.project, number=no).values_list("status", flat=True).first() or Capitulo.Status.DRAFT}
                 for no in PASOS_CAPITULO]} for row in projects]
