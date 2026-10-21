"""Perfil y entidades metodológicas de la investigación."""

from django.db import models
from django.db.models import Q

from .projects import Project


class ResearchProfile(models.Model):
    class Approach(models.TextChoices):
        CUANTITATIVO = "CUANTITATIVO", "Cuantitativo"
        CUALITATIVO = "CUALITATIVO", "Cualitativo"
        MIXTO = "MIXTO", "Mixto"

    project = models.OneToOneField(Project, on_delete=models.PROTECT, primary_key=True, related_name="profile")
    approach = models.CharField(max_length=16, choices=Approach.choices, null=True, blank=True)
    topic = models.TextField(null=True, blank=True, help_text="Idea provisional descrita por el tesista")
    ods_code = models.CharField(max_length=20, null=True, blank=True)
    unit_of_analysis = models.TextField(null=True, blank=True)
    place = models.TextField(null=True, blank=True)
    period_text = models.CharField(max_length=120, null=True, blank=True)
    problem_statement = models.TextField(null=True, blank=True)
    schema_version = models.PositiveSmallIntegerField(default=1)
    lock_version = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tesis_perfil_investigacion"
        constraints = [
            models.CheckConstraint(condition=Q(schema_version__gte=1), name="tesis_perfil_version_esquema_positiva"),
            models.CheckConstraint(
                condition=Q(approach__isnull=True) | Q(approach__in=["CUANTITATIVO", "CUALITATIVO", "MIXTO"]),
                name="tesis_perfil_enfoque_valido",
            ),
        ]


class ConsistencyRow(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="consistency_rows")
    ordinal = models.PositiveSmallIntegerField(help_text="0 para general, 1..n para específicas")
    question_text = models.TextField(null=True, blank=True)
    objective_text = models.TextField(null=True, blank=True)
    hypothesis_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tesis_fila_consistencia"
        ordering = ["ordinal"]
        constraints = [
            models.UniqueConstraint(fields=["project", "ordinal"], name="tesis_fila_consistencia_proyecto_orden_unico"),
        ]


class ResearchVariable(models.Model):
    class Role(models.TextChoices):
        INDEPENDIENTE = "INDEPENDIENTE", "Variable Independiente"
        DEPENDIENTE = "DEPENDIENTE", "Variable Dependiente"
        OTRA = "OTRA", "Otra / Constructo"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="variables")
    role = models.CharField(max_length=16, choices=Role.choices)
    name = models.CharField(max_length=200)
    conceptual_definition = models.TextField(null=True, blank=True)
    operational_definition = models.TextField(null=True, blank=True)
    ordinal = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tesis_variable_investigacion"
        ordering = ["ordinal"]
        constraints = [
            models.UniqueConstraint(fields=["project", "ordinal"], name="tesis_variable_proyecto_orden_unico"),
            models.CheckConstraint(condition=Q(ordinal__gte=1), name="tesis_variable_orden_positivo"),
            models.CheckConstraint(
                condition=Q(role__in=["INDEPENDIENTE", "DEPENDIENTE", "OTRA"]),
                name="tesis_variable_rol_valido",
            ),
        ]
        indexes = [models.Index(fields=["project", "role"], name="tesis_var_proy_rol_idx")]


class ConsistencyRowVariable(models.Model):
    consistency_row = models.ForeignKey(ConsistencyRow, on_delete=models.PROTECT, related_name="row_variables")
    variable = models.ForeignKey(ResearchVariable, on_delete=models.PROTECT, related_name="row_links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tesis_variable_fila_consistencia"
        constraints = [
            models.UniqueConstraint(
                fields=["consistency_row", "variable"],
                name="tesis_fila_variable_unica",
            ),
        ]


class VariableDimension(models.Model):
    variable = models.ForeignKey(ResearchVariable, on_delete=models.PROTECT, related_name="dimensions")
    ordinal = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=200)
    definition = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "tesis_dimension_variable"
        ordering = ["ordinal"]
        constraints = [
            models.UniqueConstraint(fields=["variable", "ordinal"], name="tesis_dimension_variable_orden_unico"),
            models.CheckConstraint(condition=Q(ordinal__gte=1), name="tesis_dimension_orden_positivo"),
        ]


class Indicator(models.Model):
    dimension = models.ForeignKey(VariableDimension, on_delete=models.PROTECT, related_name="indicators")
    ordinal = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=200)
    measurement_scale = models.CharField(max_length=30, null=True, blank=True)
    technique = models.CharField(max_length=120, null=True, blank=True)
    operational_rule = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "tesis_indicador"
        ordering = ["ordinal"]
        constraints = [
            models.UniqueConstraint(fields=["dimension", "ordinal"], name="tesis_indicador_dimension_orden_unico"),
            models.CheckConstraint(condition=Q(ordinal__gte=1), name="tesis_indicador_orden_positivo"),
        ]
