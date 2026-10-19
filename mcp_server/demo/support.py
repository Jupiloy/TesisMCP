"""Preparación y comprobación de la demostración MCP local (Capítulos 1 al 3)."""

from mcp_server.django_bridge import configurar_django


def _preparar_usuarios_y_tokens():
    """Crea o recupera los usuarios del caso semilla UTP Sede Piura y emite sus tokens MCP."""
    configurar_django()
    from asgiref.sync import sync_to_async
    from django.contrib.auth import get_user_model
    from thesis.services.mcp_auth import emitir_token

    def _preparar_entorno_sincrono():
        Usuario = get_user_model()
        student, _ = Usuario.objects.update_or_create(
            email="u202112345@utp.edu.pe",
            defaults={
                "display_name": "Josué Carrasco García (Tesista UTP Piura)",
                "is_active": True,
            },
        )
        advisor, _ = Usuario.objects.update_or_create(
            email="asesor.sistemas@utp.edu.pe",
            defaults={
                "display_name": "Dr. Carlos Ramos Mendoza (Asesor UTP Piura)",
                "is_active": True,
            },
        )
        student_token = emitir_token(student)
        advisor_token = emitir_token(advisor)
        return student.email, advisor.email, student_token, advisor_token

    return sync_to_async(_preparar_entorno_sincrono)()


def _inspeccionar_bd_relacional(project_id: str) -> dict:
    """Consulta en PostgreSQL el conteo exacto de entidades relacionales generadas por el flujo MCP."""
    configurar_django()
    from asgiref.sync import sync_to_async
    from thesis.models import (
        Capitulo,
        RevisionCapitulo,
        FilaConsistencia,
        VariableFilaConsistencia,
        Indicador,
        PerfilInvestigacion,
        VariableInvestigacion,
        ComentarioRevision,
        EventoRevision,
        ProgresoPaso,
        DimensionVariable,
    )

    def _contar_sincrono():
        profile = PerfilInvestigacion.objects.get(project_id=project_id)
        return {
            "lock_version": profile.lock_version,
            "ods_code": profile.ods_code,
            "steps_completed": ProgresoPaso.objects.filter(project_id=project_id, status="COMPLETED").count(),
            "chapters_approved": Capitulo.objects.filter(project_id=project_id, status=Capitulo.Status.APPROVED).count(),
            "chapter_revisions": RevisionCapitulo.objects.filter(chapter__project_id=project_id).count(),
            "consistency_rows": FilaConsistencia.objects.filter(project_id=project_id).count(),
            "consistency_row_vars": VariableFilaConsistencia.objects.filter(consistency_row__project_id=project_id).count(),
            "research_variables": VariableInvestigacion.objects.filter(project_id=project_id).count(),
            "variable_dimensions": DimensionVariable.objects.filter(variable__project_id=project_id).count(),
            "indicators": Indicador.objects.filter(dimension__variable__project_id=project_id).count(),
            "review_comments_resolved": ComentarioRevision.objects.filter(
                revision__chapter__project_id=project_id, status=ComentarioRevision.Status.RESOLVED
            ).count(),
            "review_events": EventoRevision.objects.filter(revision__chapter__project_id=project_id).count(),
        }

    return sync_to_async(_contar_sincrono)()
