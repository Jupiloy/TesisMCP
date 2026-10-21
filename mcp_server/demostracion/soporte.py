"""Preparación y comprobación de la demostración MCP local (Capítulos 1 al 3)."""

from mcp_server.puente_django import configurar_django


def _preparar_usuarios_y_tokens():
    """Crea o recupera los usuarios del caso semilla UTP Sede Piura y emite sus tokens MCP."""
    configurar_django()
    from asgiref.sync import sync_to_async
    from django.contrib.auth import get_user_model
    from thesis.services.autenticacion_mcp import emitir_token

    def _preparar_entorno_sincrono():
        Usuario = get_user_model()
        tesista, _ = Usuario.objects.update_or_create(
            email="u202112345@utp.edu.pe",
            defaults={
                "display_name": "Josué Carrasco García (Tesista UTP Piura)",
                "is_active": True,
            },
        )
        asesor, _ = Usuario.objects.update_or_create(
            email="asesor.sistemas@utp.edu.pe",
            defaults={
                "display_name": "Dr. Carlos Ramos Mendoza (Asesor UTP Piura)",
                "is_active": True,
            },
        )
        token_tesista = emitir_token(tesista)
        token_asesor = emitir_token(asesor)
        return tesista.email, asesor.email, token_tesista, token_asesor

    return sync_to_async(_preparar_entorno_sincrono)()


def _inspeccionar_bd_relacional(id_proyecto: str) -> dict:
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
        perfil = PerfilInvestigacion.objects.get(project_id=id_proyecto)
        return {
            "version_bloqueo": perfil.lock_version,
            "codigo_ods": perfil.ods_code,
            "pasos_completados": ProgresoPaso.objects.filter(project_id=id_proyecto, status="COMPLETADO").count(),
            "capitulos_aprobados": Capitulo.objects.filter(project_id=id_proyecto, status=Capitulo.Status.APROBADO).count(),
            "revisiones_capitulo": RevisionCapitulo.objects.filter(chapter__project_id=id_proyecto).count(),
            "filas_consistencia": FilaConsistencia.objects.filter(project_id=id_proyecto).count(),
            "cruces_fila_variable": VariableFilaConsistencia.objects.filter(consistency_row__project_id=id_proyecto).count(),
            "variables_investigacion": VariableInvestigacion.objects.filter(project_id=id_proyecto).count(),
            "dimensiones_variable": DimensionVariable.objects.filter(variable__project_id=id_proyecto).count(),
            "indicadores": Indicador.objects.filter(dimension__variable__project_id=id_proyecto).count(),
            "comentarios_resueltos": ComentarioRevision.objects.filter(
                revision__chapter__project_id=id_proyecto, status=ComentarioRevision.Status.RESUELTA
            ).count(),
            "eventos_revision": EventoRevision.objects.filter(revision__chapter__project_id=id_proyecto).count(),
        }

    return sync_to_async(_contar_sincrono)()
