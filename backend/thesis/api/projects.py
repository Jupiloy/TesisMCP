from uuid import UUID

from django.http import FileResponse
from ninja import Router, Schema

from thesis.services.discovery import buscar_semantic_scholar_servicio
from thesis.services.discovery_peru import buscar_antecedentes_peru_servicio
from thesis.services.exploration import explorar_idea_servicio
from thesis.services.exports import exportar_borrador_docx
from thesis.services.projects import crear_proyecto_servicio, obtener_estado_proyecto, registrar_idea_servicio
from thesis.services.steps import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio
from thesis.services.reviews import (
    agregar_comentario_servicio,
    panel_asesor,
    asignar_asesor_servicio,
    decidir_capitulo_servicio,
    listar_comentarios_servicio,
    resolver_comentario_servicio,
)


router = Router(tags=["Proyectos"])


class EntradaCrearProyecto(Schema):
    name: str
    title: str | None = None


class EntradaRegistrarIdea(Schema):
    description: str
    expected_version: int


class EntradaGuardarPaso(Schema):
    content_md: str
    output_data: dict
    expected_version: int
    idempotency_key: UUID


class EntradaAsignarAsesor(Schema):
    email: str


class EntradaComentario(Schema):
    start_cp: int
    end_cp: int
    selected_text: str
    body: str


class EntradaDecision(Schema):
    action: str
    reason: str = ""


@router.post("")
def crear(request, payload: EntradaCrearProyecto):
    project = crear_proyecto_servicio(request.user, payload.name, payload.title)
    return obtener_estado_proyecto(request.user, project.id)


@router.get("/{project_id}")
def estado(request, project_id: UUID):
    return obtener_estado_proyecto(request.user, project_id)


@router.get("/{project_id}/export/draft.docx")
def exportar_borrador(request, project_id: UUID):
    stream = exportar_borrador_docx(request.user, project_id)
    return FileResponse(
        stream,
        as_attachment=True,
        filename="tesis-borrador.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.put("/{project_id}/idea")
def idea(request, project_id: UUID, payload: EntradaRegistrarIdea):
    return registrar_idea_servicio(request.user, project_id, payload.description, payload.expected_version)


@router.get("/{project_id}/idea/explore")
def explorar(request, project_id: UUID):
    return explorar_idea_servicio(request.user, project_id)


@router.get("/{project_id}/discovery/semantic-scholar")
def semantic_scholar(request, project_id: UUID, query: str, limit: int = 5):
    return buscar_semantic_scholar_servicio(request.user, project_id, query, limit)


@router.get("/{project_id}/discovery/peru")
def antecedentes_peru(
    request,
    project_id: UUID,
    query: str,
    scope_filter: str = "todos",
    include_articles: bool = True,
    limit: int = 5,
):
    return buscar_antecedentes_peru_servicio(
        request.user,
        project_id,
        query,
        scope_filter=scope_filter,
        include_articles=include_articles,
        limit=limit,
    )


@router.post("/{project_id}/advisor")
def establecer_asesor(request, project_id: UUID, payload: EntradaAsignarAsesor):
    return asignar_asesor_servicio(request.user, project_id, payload.email)


@router.get("/advisor/dashboard")
def proyectos_asesor(request):
    return panel_asesor(request.user)


@router.put("/{project_id}/steps/{step_code}")
def guardar_paso_proyecto(request, project_id: UUID, step_code: str, payload: EntradaGuardarPaso):
    return guardar_paso_servicio(
        request.user,
        project_id,
        step_code,
        payload.content_md,
        payload.output_data,
        payload.expected_version,
        str(payload.idempotency_key),
    )


@router.get("/{project_id}/chapters/{chapter_no}")
def estado_capitulo(request, project_id: UUID, chapter_no: int):
    return obtener_capitulo_servicio(request.user, project_id, chapter_no)


@router.post("/{project_id}/chapters/{chapter_no}/submit")
def enviar_capitulo_proyecto(request, project_id: UUID, chapter_no: int):
    return enviar_capitulo_servicio(request.user, project_id, chapter_no)


@router.post("/{project_id}/chapters/{chapter_no}/comments")
def agregar_comentario_revision(request, project_id: UUID, chapter_no: int, payload: EntradaComentario):
    return agregar_comentario_servicio(
        request.user,
        project_id,
        chapter_no,
        payload.start_cp,
        payload.end_cp,
        payload.selected_text,
        payload.body,
    )


@router.get("/{project_id}/chapters/{chapter_no}/comments")
def comentarios_revision(request, project_id: UUID, chapter_no: int):
    return listar_comentarios_servicio(request.user, project_id, chapter_no)


@router.post("/{project_id}/comments/{comment_id}/resolve")
def resolver_comentario_revision(request, project_id: UUID, comment_id: int):
    return resolver_comentario_servicio(request.user, project_id, comment_id)


@router.post("/{project_id}/chapters/{chapter_no}/decision")
def decision_revision(request, project_id: UUID, chapter_no: int, payload: EntradaDecision):
    return decidir_capitulo_servicio(request.user, project_id, chapter_no, payload.action, payload.reason)
