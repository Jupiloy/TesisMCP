"""Proyectos de tesis y participantes."""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Activo"
        ARCHIVED = "ARCHIVED", "Archivado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    title = models.CharField(max_length=300)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tesis_proyecto"
        indexes = [models.Index(fields=["status", "-updated_at"], name="tesis_proy_estado_act_idx")]

    def __str__(self):
        return self.name


class ProjectParticipant(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Tesista"
        ADVISOR = "ADVISOR", "Asesor"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    role = models.CharField(max_length=10, choices=Role.choices)
    active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tesis_participante_proyecto"
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="tesis_participante_proyecto_usuario_unico"),
            models.UniqueConstraint(fields=["project"], condition=Q(role="OWNER", active=True), name="tesis_participante_un_propietario_activo"),
            models.UniqueConstraint(fields=["project"], condition=Q(role="ADVISOR", active=True), name="tesis_participante_un_asesor_activo"),
            models.CheckConstraint(condition=Q(active=True, left_at__isnull=True) | Q(active=False, left_at__isnull=False), name="tesis_participante_fechas_activas_coinciden"),
        ]
        indexes = [models.Index(fields=["user", "active", "role"], name="tesis_part_usuario_rol_idx")]
