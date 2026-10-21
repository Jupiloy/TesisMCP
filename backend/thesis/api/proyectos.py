from uuid import UUID

from django.http import FileResponse
from ninja import Router, Schema

from thesis.services.descubrimiento import buscar_semantic_scholar_servicio
from thesis.services.descubrimiento_peru import buscar_antecedentes_peru_servicio
from thesis.services.exploracion import explorar_idea_servicio
from thesis.services.exportaciones import exportar_borrador_docx
from thesis.services.proyectos import (
    crear_proyecto_servicio,
    listar_proyectos_servicio,
    obtener_estado_proyecto,
    registrar_idea_servicio,
)
from thesis.services.pasos import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio
from thesis.services.revisiones import (
    agregar_comentario_servicio,
    asignar_asesor_servicio,
    decidir_capitulo_servicio,
    listar_comentarios_servicio,
    resolver_comentario_servicio,
)


router = Router(tags=["Proyectos"])


class EntradaCrearProyecto(Schema):
    nombre: str
    titulo: str | None = None


class EntradaRegistrarIdea(Schema):
    descripcion: str
    version_esperada: int


class EntradaGuardarPaso(Schema):
    contenido_md: str
    datos_salida: dict
    version_esperada: int
    clave_idempotencia: UUID


class EntradaAsignarAsesor(Schema):
    correo: str


class EntradaComentario(Schema):
    inicio_caracter: int
    fin_caracter: int
    texto_seleccionado: str
    contenido: str


class EntradaDecision(Schema):
    accion: str
    motivo: str = ""


@router.post("")
def crear(request, entrada: EntradaCrearProyecto):
    proyecto = crear_proyecto_servicio(request.user, entrada.nombre, entrada.titulo)
    return obtener_estado_proyecto(request.user, proyecto.id)


@router.get("")
def listar(request):
    return listar_proyectos_servicio(request.user)


@router.get("/{id_proyecto}")
def estado(request, id_proyecto: UUID):
    return obtener_estado_proyecto(request.user, id_proyecto)


@router.get("/{id_proyecto}/exportar/borrador.docx")
def exportar_borrador(request, id_proyecto: UUID):
    flujo = exportar_borrador_docx(request.user, id_proyecto)
    return FileResponse(
        flujo,
        as_attachment=True,
        filename="tesis-borrador.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.put("/{id_proyecto}/idea")
def idea(request, id_proyecto: UUID, entrada: EntradaRegistrarIdea):
    return registrar_idea_servicio(request.user, id_proyecto, entrada.descripcion, entrada.version_esperada)


@router.get("/{id_proyecto}/idea/explorar")
def explorar(request, id_proyecto: UUID):
    return explorar_idea_servicio(request.user, id_proyecto)


@router.get("/{id_proyecto}/descubrimiento/semantic-scholar")
def semantic_scholar(request, id_proyecto: UUID, consulta: str, limite: int = 5):
    return buscar_semantic_scholar_servicio(request.user, id_proyecto, consulta, limite)


@router.get("/{id_proyecto}/descubrimiento/peru")
def antecedentes_peru(
    request,
    id_proyecto: UUID,
    consulta: str,
    filtro_alcance: str = "todos",
    incluir_articulos: bool = True,
    limite: int = 5,
):
    return buscar_antecedentes_peru_servicio(
        request.user,
        id_proyecto,
        consulta,
        filtro_alcance=filtro_alcance,
        incluir_articulos=incluir_articulos,
        limite=limite,
    )


@router.post("/{id_proyecto}/asesor")
def establecer_asesor(request, id_proyecto: UUID, entrada: EntradaAsignarAsesor):
    return asignar_asesor_servicio(request.user, id_proyecto, entrada.correo)


@router.put("/{id_proyecto}/pasos/{codigo_paso}")
def guardar_paso_proyecto(request, id_proyecto: UUID, codigo_paso: str, entrada: EntradaGuardarPaso):
    return guardar_paso_servicio(
        request.user,
        id_proyecto,
        codigo_paso,
        entrada.contenido_md,
        entrada.datos_salida,
        entrada.version_esperada,
        str(entrada.clave_idempotencia),
    )


@router.get("/{id_proyecto}/capitulos/{numero_capitulo}")
def estado_capitulo(request, id_proyecto: UUID, numero_capitulo: int):
    return obtener_capitulo_servicio(request.user, id_proyecto, numero_capitulo)


@router.post("/{id_proyecto}/capitulos/{numero_capitulo}/enviar")
def enviar_capitulo_proyecto(request, id_proyecto: UUID, numero_capitulo: int):
    return enviar_capitulo_servicio(request.user, id_proyecto, numero_capitulo)


@router.post("/{id_proyecto}/capitulos/{numero_capitulo}/comentarios")
def agregar_comentario_revision(request, id_proyecto: UUID, numero_capitulo: int, entrada: EntradaComentario):
    return agregar_comentario_servicio(
        request.user,
        id_proyecto,
        numero_capitulo,
        entrada.inicio_caracter,
        entrada.fin_caracter,
        entrada.texto_seleccionado,
        entrada.contenido,
    )


@router.get("/{id_proyecto}/capitulos/{numero_capitulo}/comentarios")
def comentarios_revision(request, id_proyecto: UUID, numero_capitulo: int):
    return listar_comentarios_servicio(request.user, id_proyecto, numero_capitulo)


@router.post("/{id_proyecto}/comentarios/{id_comentario}/resolver")
def resolver_comentario_revision(request, id_proyecto: UUID, id_comentario: int):
    return resolver_comentario_servicio(request.user, id_proyecto, id_comentario)


@router.post("/{id_proyecto}/capitulos/{numero_capitulo}/decision")
def decision_revision(request, id_proyecto: UUID, numero_capitulo: int, entrada: EntradaDecision):
    return decidir_capitulo_servicio(request.user, id_proyecto, numero_capitulo, entrada.accion, entrada.motivo)
