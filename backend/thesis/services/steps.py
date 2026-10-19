"""Guardado de pasos y revisiones académicas del MVP."""

import hashlib
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from pydantic import ValidationError

from thesis.models import Capitulo, RevisionCapitulo, PerfilInvestigacion, EventoRevision, ProgresoPaso
from thesis.services.access import requerir_proyecto
from thesis.services.errors import ErrorDominio
from thesis.services.step_contracts import CONTRATOS
from thesis.services.step_materializers import ejecutar_materializador_paso
from thesis.step_catalogue import CATALOGO_PASOS


PASOS_CAPITULO = {
    chapter: [code for code, info in CATALOGO_PASOS.items() if info["capitulo"] == chapter]
    for chapter in sorted({info["capitulo"] for info in CATALOGO_PASOS.values()})
}


def _datos_revision(revision: RevisionCapitulo) -> dict:
    return {"revision_id": revision.pk, "revision_no": revision.revision_no,
            "chapter_no": revision.chapter.number, "step_code": revision.step_code,
            "content_md": revision.content_md, "content_sha256": revision.content_sha256,
            "created_at": revision.created_at.isoformat()}


def obtener_capitulo_servicio(actor, project_id, chapter_no: int) -> dict:
    project = requerir_proyecto(actor, project_id)
    if chapter_no not in PASOS_CAPITULO:
        raise ErrorDominio("NOT_FOUND", "Capítulo no disponible en la plataforma")
    chapter = Capitulo.objects.filter(project=project, number=chapter_no).first()
    latest = chapter.revisions.order_by("-revision_no").first() if chapter else None
    return {"chapter_no": chapter_no, "status": chapter.status if chapter else Capitulo.Status.DRAFT,
            "latest_revision": _datos_revision(latest) if latest else None,
            "approved_revision_id": chapter.approved_revision_id if chapter else None,
            "steps": list(ProgresoPaso.objects.filter(project=project, step_code__in=PASOS_CAPITULO[chapter_no])
                          .order_by("step_code").values("step_code", "status", "output_json"))}


def guardar_paso_servicio(actor, project_id, step_code: str, content_md: str, output_data: dict,
              expected_version: int, idempotency_key: str) -> dict:
    project = requerir_proyecto(actor, project_id, owner_only=True)
    if step_code not in CONTRATOS:
        raise ErrorDominio("VALIDATION_ERROR", f"Paso {step_code} no disponible en el catálogo de pasos")
    chapter_no = next((ch for ch, steps in PASOS_CAPITULO.items() if step_code in steps), None)
    if chapter_no is None:
        raise ErrorDominio("VALIDATION_ERROR", f"Capítulo no encontrado para {step_code}")
    try:
        key = UUID(str(idempotency_key))
    except (ValueError, TypeError) as exc:
        raise ErrorDominio("VALIDATION_ERROR", "idempotency_key debe ser UUID") from exc
    content_md = content_md.strip()
    if not content_md or len(content_md) > 200000:
        raise ErrorDominio("VALIDATION_ERROR", "El contenido de la revisión debe tener entre 1 y 200000 caracteres")
    if step_code == "P04" and len(str(output_data.get("titulo_oficial", "")).split()) > 20:
        raise ErrorDominio("RULE_WORD_COUNT_EXCEEDED", "El título supera el máximo de 20 palabras")
    if step_code == "P06":
        question = str(output_data.get("pregunta_general", "")).strip()
        if not question.startswith("¿") or not question.endswith("?"):
            raise ErrorDominio("RULE_QUESTION_FORMAT", "La pregunta general requiere signos ¿?")
    try:
        validated = CONTRATOS[step_code].model_validate(output_data).model_dump()
    except ValidationError as exc:
        raise ErrorDominio("VALIDATION_SCHEMA_ERROR", str(exc)[:1000]) from exc
    with transaction.atomic():
        profile = PerfilInvestigacion.objects.select_for_update().get(project=project)
        chapter, _ = Capitulo.objects.get_or_create(project=project, number=chapter_no)
        chapter = Capitulo.objects.select_for_update().get(pk=chapter.pk)
        existing = RevisionCapitulo.objects.filter(chapter=chapter, idempotency_key=key).first()
        if existing:
            if existing.step_code != step_code or existing.content_md != content_md:
                raise ErrorDominio("VERSION_CONFLICT", "La clave de idempotencia ya corresponde a otra revisión")
            return {**_datos_revision(existing), "state_version": profile.lock_version, "idempotent": True}
        if profile.lock_version != expected_version:
            raise ErrorDominio("VERSION_CONFLICT", "El perfil cambió; consulta la versión actual")
        if chapter.status not in (Capitulo.Status.DRAFT, Capitulo.Status.CHANGES_REQUESTED):
            raise ErrorDominio("VERSION_CONFLICT", "El capítulo debe volver a borrador antes de editarse")
        sequence = [step for steps in PASOS_CAPITULO.values() for step in steps]
        if step_code != "P01":
            previous = sequence[sequence.index(step_code) - 1]
            if not ProgresoPaso.objects.filter(project=project, step_code=previous, status=ProgresoPaso.Status.COMPLETED).exists():
                raise ErrorDominio("PREREQUISITE_LOCKED", f"Completa {previous} antes de {step_code}")
        ejecutar_materializador_paso(project, profile, step_code, validated)
        if chapter.status == Capitulo.Status.CHANGES_REQUESTED:
            chapter.resume_editing()
            chapter.save(update_fields=["status", "updated_at"])
        previous_revision = chapter.revisions.order_by("-revision_no").first()
        revision = RevisionCapitulo.objects.create(
            chapter=chapter, revision_no=(previous_revision.revision_no + 1 if previous_revision else 1),
            step_code=step_code, idempotency_key=key, content_md=content_md,
            content_sha256=hashlib.sha256(content_md.encode("utf-8")).hexdigest(), created_by=actor,
        )
        ProgresoPaso.objects.update_or_create(project=project, step_code=step_code, defaults={
            "status": ProgresoPaso.Status.COMPLETED, "output_json": validated, "completed_at": timezone.now(),
        })
        profile.lock_version += 1
        profile.save(update_fields=[
            "lock_version", "problem_statement", "ods_code",
            "unit_of_analysis", "place", "period_text", "approach", "updated_at",
        ])
        return {**_datos_revision(revision), "state_version": profile.lock_version, "idempotent": False}


def enviar_capitulo_servicio(actor, project_id, chapter_no: int) -> dict:
    project = requerir_proyecto(actor, project_id, owner_only=True)
    if chapter_no not in PASOS_CAPITULO:
        raise ErrorDominio("NOT_FOUND", "Capítulo no disponible en la plataforma")
    with transaction.atomic():
        chapter = Capitulo.objects.select_for_update().filter(project=project, number=chapter_no).first()
        if chapter is None or chapter.status != Capitulo.Status.DRAFT:
            raise ErrorDominio("VERSION_CONFLICT", "El capítulo no está listo para enviar")
        completed = set(ProgresoPaso.objects.filter(
            project=project, step_code__in=PASOS_CAPITULO[chapter_no], status=ProgresoPaso.Status.COMPLETED,
        ).values_list("step_code", flat=True))
        if completed != set(PASOS_CAPITULO[chapter_no]):
            raise ErrorDominio("PREREQUISITE_LOCKED", "Completa todos los pasos del capítulo")
        revision = chapter.revisions.order_by("-revision_no").first()
        if revision is None:
            raise ErrorDominio("PREREQUISITE_LOCKED", "Guarda una revisión antes de enviarla")
        chapter.submit()
        chapter.save(update_fields=["status", "updated_at"])
        EventoRevision.objects.create(chapter=chapter, revision=revision, actor=actor, action=EventoRevision.Action.SUBMIT)
    return obtener_capitulo_servicio(actor, project_id, chapter_no)
