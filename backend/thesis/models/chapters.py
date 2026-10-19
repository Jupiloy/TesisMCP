"""Avance, revisiones y decisiones del asesor (Capítulos 1 al 3)."""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django_fsm import FSMField, FSMModelMixin, transition

from .projects import Project


class StepProgress(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "En curso"
        COMPLETED = "COMPLETED", "Completado"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="steps")
    step_code = models.CharField(max_length=3)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.IN_PROGRESS)
    output_json = models.JSONField(default=dict)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tesis_progreso_paso"
        constraints = [models.UniqueConstraint(fields=["project", "step_code"], name="tesis_paso_proyecto_codigo_unico")]


class Chapter(FSMModelMixin, models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Borrador"
        READY = "READY", "En revisión"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Con observaciones"
        APPROVED = "APPROVED", "Aprobado"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="chapters")
    number = models.PositiveSmallIntegerField()
    status = FSMField(default=Status.DRAFT, protected=True, choices=Status.choices)
    approved_revision = models.ForeignKey("ChapterRevision", on_delete=models.PROTECT, null=True, blank=True, related_name="approving_chapters")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transition(field=status, source=[Status.DRAFT, Status.CHANGES_REQUESTED], target=Status.READY)
    def submit(self):
        pass

    @transition(field=status, source=Status.READY, target=Status.CHANGES_REQUESTED)
    def request_changes(self):
        pass

    @transition(field=status, source=Status.READY, target=Status.APPROVED)
    def approve(self):
        pass

    @transition(field=status, source=Status.APPROVED, target=Status.DRAFT)
    def reopen(self):
        pass

    @transition(field=status, source=Status.CHANGES_REQUESTED, target=Status.DRAFT)
    def resume_editing(self):
        pass

    class Meta:
        db_table = "tesis_capitulo"
        constraints = [
            models.UniqueConstraint(fields=["project", "number"], name="tesis_capitulo_proyecto_numero_unico"),
            models.CheckConstraint(condition=Q(number__gte=1, number__lte=3), name="tesis_capitulo_numero_rango"),
        ]


class ChapterRevision(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT, related_name="revisions")
    revision_no = models.PositiveIntegerField()
    step_code = models.CharField(max_length=3)
    idempotency_key = models.UUIDField()
    content_md = models.TextField()
    content_sha256 = models.CharField(max_length=64)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tesis_revision_capitulo"
        constraints = [
            models.UniqueConstraint(fields=["chapter", "revision_no"], name="tesis_revision_capitulo_numero_unico"),
            models.UniqueConstraint(fields=["chapter", "idempotency_key"], name="tesis_revision_capitulo_clave_unica"),
            models.CheckConstraint(condition=Q(revision_no__gt=0), name="tesis_revision_numero_positivo"),
            models.CheckConstraint(condition=~Q(content_md=""), name="tesis_revision_contenido_no_vacio"),
        ]


class ReviewComment(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Abierta"
        RESOLVED = "RESOLVED", "Resuelta"

    revision = models.ForeignKey(ChapterRevision, on_delete=models.PROTECT, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="authored_comments")
    start_cp = models.PositiveIntegerField()
    end_cp = models.PositiveIntegerField()
    selected_text = models.TextField()
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="resolved_comments")
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tesis_comentario_revision"
        constraints = [models.CheckConstraint(condition=Q(end_cp__gt=models.F("start_cp")), name="tesis_comentario_rango_positivo")]
        indexes = [models.Index(fields=["revision", "status", "created_at"], name="tesis_comentario_estado_idx")]


class ReviewEvent(models.Model):
    class Action(models.TextChoices):
        SUBMIT = "SUBMIT", "Enviado"
        REQUEST_CHANGES = "REQUEST_CHANGES", "Observado"
        APPROVE = "APPROVE", "Aprobado"
        REOPEN = "REOPEN", "Reabierto"

    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT, related_name="review_events")
    revision = models.ForeignKey(ChapterRevision, on_delete=models.PROTECT, null=True, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tesis_evento_revision"
        indexes = [models.Index(fields=["chapter", "created_at"], name="tesis_evento_capitulo_idx")]
