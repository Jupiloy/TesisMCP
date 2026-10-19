"""Adaptadores MCP para los Capítulos 1 al 3 y exploración inicial: sus reglas viven en thesis.services."""

from typing import Any
from uuid import UUID

from mcp.server.mcpserver.exceptions import ToolError

from mcp_server.django_bridge import usuario_actual, configurar_django


def _invocar(operacion, *args, **kwargs):
    from django.db import connections
    from thesis.services.errors import ErrorDominio

    try:
        return operacion(usuario_actual(), *args, **kwargs)
    except ErrorDominio as exc:
        raise ToolError(f"{exc.code}: {exc.message}") from exc
    finally:
        connections.close_all()


def _uuid_proyecto(project_id: str) -> UUID:
    try:
        return UUID(project_id)
    except ValueError as exc:
        raise ToolError("VALIDATION_ERROR: project_id debe ser UUID") from exc


def registrar_herramientas_proyecto(app) -> None:
    configurar_django()
    from thesis.services.discovery import buscar_semantic_scholar_servicio
    from thesis.services.discovery_peru import buscar_antecedentes_peru_servicio
    from thesis.services.exploration import explorar_idea_servicio
    from thesis.services.projects import crear_proyecto_servicio, obtener_estado_proyecto, registrar_idea_servicio
    from thesis.services.reviews import (
        agregar_comentario_servicio,
        asignar_asesor_servicio,
        decidir_capitulo_servicio,
        listar_comentarios_servicio,
        resolver_comentario_servicio,
    )
    from thesis.services.steps import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio

    @app.tool()
    def crear_proyecto(name: str, title: str | None = None) -> dict[str, Any]:
        """Crea un proyecto para el usuario autenticado del cliente MCP."""
        def operacion(actor):
            project = crear_proyecto_servicio(actor, name, title)
            return obtener_estado_proyecto(actor, project.id)

        return _invocar(operacion)

    @app.tool()
    def obtener_estado(project_id: str) -> dict[str, Any]:
        """Consulta el estado de un proyecto al que pertenece el usuario."""
        return _invocar(obtener_estado_proyecto, _uuid_proyecto(project_id))

    @app.tool()
    def registrar_idea(project_id: str, description: str, expected_version: int) -> dict[str, Any]:
        """Guarda una idea provisional confirmada por el tesista, con control de versión."""
        return _invocar(registrar_idea_servicio, _uuid_proyecto(project_id), description, expected_version)

    @app.tool()
    def explorar_idea(project_id: str) -> dict[str, Any]:
        """Busca literatura sobre la idea guardada; devuelve solo metadatos, no resultados demostrados."""
        return _invocar(explorar_idea_servicio, _uuid_proyecto(project_id))

    @app.tool()
    def buscar_semantic_scholar(project_id: str, query: str, limit: int = 5) -> dict[str, Any]:
        """Busca metadatos en Semantic Scholar; no inspecciona ni verifica el texto completo."""
        return _invocar(buscar_semantic_scholar_servicio, _uuid_proyecto(project_id), query, limit)

    @app.tool()
    def buscar_antecedentes_peru(
        project_id: str,
        query: str,
        scope_filter: str = "todos",
        include_articles: bool = True,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Busca tesis en ALICIA y artículos con filiación peruana; no acredita revisión por pares ni inspección del PDF."""
        return _invocar(
            buscar_antecedentes_peru_servicio,
            _uuid_proyecto(project_id),
            query,
            scope_filter=scope_filter,
            include_articles=include_articles,
            limit=limit,
        )

    @app.tool()
    def guardar_paso(
        project_id: str,
        step_code: str,
        content_md: str,
        output_data: dict[str, Any],
        expected_version: int,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Valida P01-P12 (Capítulos 1 al 3) y guarda una revisión completa confirmada por el tesista."""
        return _invocar(
            guardar_paso_servicio,
            _uuid_proyecto(project_id),
            step_code,
            content_md,
            output_data,
            expected_version,
            idempotency_key,
        )

    @app.tool()
    def consultar_capitulo(project_id: str, chapter_no: int) -> dict[str, Any]:
        """Lee progreso y revisión vigente de un capítulo autorizado (1 al 3)."""
        return _invocar(obtener_capitulo_servicio, _uuid_proyecto(project_id), chapter_no)

    @app.tool()
    def enviar_capitulo(project_id: str, chapter_no: int) -> dict[str, Any]:
        """Envía al asesor un capítulo (1 al 3) cuyos pasos están completos."""
        return _invocar(enviar_capitulo_servicio, _uuid_proyecto(project_id), chapter_no)

    @app.tool()
    def asignar_asesor(project_id: str, email: str) -> dict[str, Any]:
        """Asigna un usuario existente como asesor activo del proyecto del tesista."""
        return _invocar(asignar_asesor_servicio, _uuid_proyecto(project_id), email)

    @app.tool()
    def consultar_observaciones(project_id: str, chapter_no: int) -> list[dict[str, Any]]:
        """Lista comentarios anclados a revisiones de un capítulo autorizado."""
        return _invocar(listar_comentarios_servicio, _uuid_proyecto(project_id), chapter_no)

    @app.tool()
    def observar_fragmento(
        project_id: str,
        chapter_no: int,
        start_cp: int,
        end_cp: int,
        selected_text: str,
        body: str,
    ) -> dict[str, Any]:
        """El asesor comenta un fragmento exacto de la revisión vigente."""
        return _invocar(
            agregar_comentario_servicio,
            _uuid_proyecto(project_id),
            chapter_no,
            start_cp,
            end_cp,
            selected_text,
            body,
        )

    @app.tool()
    def decidir_capitulo(project_id: str, chapter_no: int, action: str, reason: str = "") -> dict[str, Any]:
        """El asesor solicita cambios, aprueba o reabre un capítulo con las guardas del dominio."""
        return _invocar(decidir_capitulo_servicio, _uuid_proyecto(project_id), chapter_no, action, reason)

    @app.tool()
    def resolver_observacion(project_id: str, comment_id: int) -> dict[str, Any]:
        """El asesor marca como resuelta una observación del proyecto."""
        return _invocar(resolver_comentario_servicio, _uuid_proyecto(project_id), comment_id)
