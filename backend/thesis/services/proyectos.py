from django.db import transaction
from django.db.models import F
from django.utils import timezone

from thesis.models import Proyecto, ParticipanteProyecto, PerfilInvestigacion, ProgresoPaso, RevisionCapitulo
from thesis.services.acceso import requerir_proyecto
from thesis.services.errores import ErrorDominio
from thesis.catalogo_pasos import CATALOGO_PASOS


def _limpiar_texto(valor: str, nombre: str, longitud_maxima: int) -> str:
    texto_limpio = valor.strip()
    if not texto_limpio or len(texto_limpio) > longitud_maxima:
        raise ErrorDominio("ERROR_VALIDACION", f"{nombre} debe tener entre 1 y {longitud_maxima} caracteres")
    return texto_limpio


@transaction.atomic
def crear_proyecto_servicio(usuario, nombre: str, titulo: str | None = None) -> Proyecto:
    proyecto = Proyecto.objects.create(
        name=_limpiar_texto(nombre, "nombre", 160),
        title=_limpiar_texto(titulo, "titulo", 300) if titulo else "Título por definir",
    )
    ParticipanteProyecto.objects.create(
        project=proyecto,
        user=usuario,
        role=ParticipanteProyecto.Role.TESISTA,
    )
    PerfilInvestigacion.objects.create(project=proyecto)
    return proyecto


def listar_proyectos_servicio(usuario) -> list[dict]:
    """Lista únicamente los proyectos activos que pertenecen al tesista autenticado."""
    proyectos = (
        Proyecto.objects.filter(
            participants__user=usuario,
            participants__role=ParticipanteProyecto.Role.TESISTA,
            participants__active=True,
            status=Proyecto.Status.ACTIVO,
        )
        .select_related("profile")
        .order_by("-updated_at", "name")
    )
    return [
        {
            "id_proyecto": str(proyecto.id),
            "nombre": proyecto.name,
            "titulo": proyecto.title,
            "estado": proyecto.status,
            "version_estado": proyecto.profile.lock_version,
            "actualizado_en": proyecto.updated_at.isoformat(),
        }
        for proyecto in proyectos
    ]


def _estado_pasos(proyecto: Proyecto) -> list[dict]:
    codigos = list(CATALOGO_PASOS)
    progresos = {
        progreso.step_code: progreso
        for progreso in ProgresoPaso.objects.filter(project=proyecto, step_code__in=codigos)
    }
    revisiones = {}
    for revision in (
        RevisionCapitulo.objects.filter(chapter__project=proyecto, step_code__in=codigos)
        .order_by("step_code", "-revision_no")
    ):
        revisiones.setdefault(revision.step_code, revision)

    resultado = []
    for indice, codigo in enumerate(codigos):
        progreso = progresos.get(codigo)
        dependencia = codigos[indice - 1] if indice else None
        completado = progreso is not None and progreso.status == ProgresoPaso.Status.COMPLETADO
        disponible = dependencia is None or dependencia in progresos and (
            progresos[dependencia].status == ProgresoPaso.Status.COMPLETADO
        )
        revision = revisiones.get(codigo)
        resultado.append(
            {
                "codigo": codigo,
                "estado": "COMPLETADO" if completado else "DISPONIBLE" if disponible else "BLOQUEADO",
                "dependencias": [dependencia] if dependencia else [],
                "acciones_permitidas": ["GUARDAR"] if disponible else [],
                "datos_salida": progreso.output_json if progreso else None,
                "contenido_md": revision.content_md if revision else "",
            }
        )
    return resultado


def obtener_estado_proyecto(usuario, id_proyecto) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto)
    perfil = proyecto.profile
    filas_consistencia = [
        {
            "orden": fila.ordinal,
            "texto_objetivo": fila.objective_text,
            "texto_pregunta": fila.question_text,
            "texto_hipotesis": fila.hypothesis_text,
        }
        for fila in proyecto.consistency_rows.order_by("ordinal")
    ]
    variables = [
        {
            "orden": variable.ordinal,
            "rol": variable.role,
            "nombre": variable.name,
            "definicion_conceptual": variable.conceptual_definition,
            "definicion_operacional": variable.operational_definition,
            "dimensiones": [
                {
                    "orden": dimension.ordinal,
                    "nombre": dimension.name,
                    "indicadores": [
                        {
                            "orden": indicador.ordinal,
                            "nombre": indicador.name,
                            "escala_medicion": indicador.measurement_scale,
                        }
                        for indicador in dimension.indicators.order_by("ordinal")
                    ],
                }
                for dimension in variable.dimensions.order_by("ordinal")
            ],
        }
        for variable in proyecto.variables.order_by("ordinal")
    ]
    return {
        "id_proyecto": str(proyecto.id),
        "nombre": proyecto.name,
        "titulo": proyecto.title,
        "estado": proyecto.status,
        "idea_provisional": perfil.topic,
        "planteamiento_problema": perfil.problem_statement,
        "codigo_ods": perfil.ods_code,
        "unidad_analisis": perfil.unit_of_analysis,
        "lugar": perfil.place,
        "periodo_texto": perfil.period_text,
        "enfoque": perfil.approach,
        "matriz_consistencia": filas_consistencia,
        "variables": variables,
        "pasos": _estado_pasos(proyecto),
        "version_estado": perfil.lock_version,
    }


@transaction.atomic
def registrar_idea_servicio(usuario, id_proyecto, descripcion: str, version_esperada: int) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto, solo_tesista=True)
    idea = _limpiar_texto(descripcion, "descripcion", 2000)
    actualizados = PerfilInvestigacion.objects.filter(
        project=proyecto, lock_version=version_esperada,
    ).update(topic=idea, lock_version=F("lock_version") + 1, updated_at=timezone.now())
    if not actualizados:
        raise ErrorDominio("CONFLICTO_VERSION", "La idea cambió; consulta el estado actual antes de guardar")
    return obtener_estado_proyecto(usuario, proyecto.id)
