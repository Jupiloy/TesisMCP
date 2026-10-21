"""Guardado de pasos y revisiones académicas del MVP."""

import hashlib
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from pydantic import ValidationError

from thesis.models import Capitulo, RevisionCapitulo, PerfilInvestigacion, EventoRevision, ProgresoPaso
from thesis.services.acceso import requerir_proyecto
from thesis.services.errores import ErrorDominio
from thesis.services.contratos_pasos import CONTRATOS
from thesis.services.materializadores_pasos import ejecutar_materializador_paso
from thesis.catalogo_pasos import CATALOGO_PASOS


PASOS_CAPITULO = {
    capitulo: [codigo for codigo, datos in CATALOGO_PASOS.items() if datos["capitulo"] == capitulo]
    for capitulo in sorted({datos["capitulo"] for datos in CATALOGO_PASOS.values()})
}


def _datos_revision(revision: RevisionCapitulo) -> dict:
    return {
        "id_revision": revision.pk,
        "numero_revision": revision.revision_no,
        "numero_capitulo": revision.chapter.number,
        "codigo_paso": revision.step_code,
        "contenido_md": revision.content_md,
        "contenido_sha256": revision.content_sha256,
        "creado_en": revision.created_at.isoformat(),
    }


def obtener_capitulo_servicio(usuario, id_proyecto, numero_capitulo: int) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto)
    if numero_capitulo not in PASOS_CAPITULO:
        raise ErrorDominio("NO_ENCONTRADO", "Capítulo no disponible en la plataforma")
    capitulo = Capitulo.objects.filter(project=proyecto, number=numero_capitulo).first()
    revision_actual = capitulo.revisions.order_by("-revision_no").first() if capitulo else None
    progresos = ProgresoPaso.objects.filter(
        project=proyecto,
        step_code__in=PASOS_CAPITULO[numero_capitulo],
    ).order_by("step_code")
    return {
        "numero_capitulo": numero_capitulo,
        "estado": capitulo.status if capitulo else Capitulo.Status.BORRADOR,
        "revision_actual": _datos_revision(revision_actual) if revision_actual else None,
        "id_revision_aprobada": capitulo.approved_revision_id if capitulo else None,
        "pasos": [
            {
                "codigo": progreso.step_code,
                "estado": progreso.status,
                "datos_salida": progreso.output_json,
            }
            for progreso in progresos
        ],
    }


def guardar_paso_servicio(
    usuario,
    id_proyecto,
    codigo_paso: str,
    contenido_md: str,
    datos_salida: dict,
    version_esperada: int,
    clave_idempotencia: str,
) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto, solo_tesista=True)
    if codigo_paso not in CONTRATOS:
        raise ErrorDominio("ERROR_VALIDACION", f"Paso {codigo_paso} no disponible en el catálogo de pasos")
    numero_capitulo = next(
        (capitulo for capitulo, pasos in PASOS_CAPITULO.items() if codigo_paso in pasos),
        None,
    )
    if numero_capitulo is None:
        raise ErrorDominio("ERROR_VALIDACION", f"Capítulo no encontrado para {codigo_paso}")
    try:
        clave = UUID(str(clave_idempotencia))
    except (ValueError, TypeError) as error:
        raise ErrorDominio("ERROR_VALIDACION", "clave_idempotencia debe ser UUID") from error
    contenido_md = contenido_md.strip()
    if not contenido_md or len(contenido_md) > 200000:
        raise ErrorDominio("ERROR_VALIDACION", "El contenido de la revisión debe tener entre 1 y 200000 caracteres")
    if codigo_paso == "P04" and len(str(datos_salida.get("titulo_oficial", "")).split()) > 20:
        raise ErrorDominio("LIMITE_PALABRAS_EXCEDIDO", "El título supera el máximo de 20 palabras")
    if codigo_paso == "P06":
        pregunta = str(datos_salida.get("pregunta_general", "")).strip()
        if not pregunta.startswith("¿") or not pregunta.endswith("?"):
            raise ErrorDominio("FORMATO_PREGUNTA_INVALIDO", "La pregunta general requiere signos ¿?")
    try:
        datos_validados = CONTRATOS[codigo_paso].model_validate(datos_salida).model_dump()
    except ValidationError as error:
        raise ErrorDominio("ERROR_ESQUEMA_VALIDACION", str(error)[:1000]) from error
    with transaction.atomic():
        perfil = PerfilInvestigacion.objects.select_for_update().get(project=proyecto)
        capitulo, _ = Capitulo.objects.get_or_create(project=proyecto, number=numero_capitulo)
        capitulo = Capitulo.objects.select_for_update().get(pk=capitulo.pk)
        existente = RevisionCapitulo.objects.filter(chapter=capitulo, idempotency_key=clave).first()
        if existente:
            if existente.step_code != codigo_paso or existente.content_md != contenido_md:
                raise ErrorDominio("CONFLICTO_VERSION", "La clave de idempotencia ya corresponde a otra revisión")
            return {**_datos_revision(existente), "version_estado": perfil.lock_version, "idempotente": True}
        if perfil.lock_version != version_esperada:
            raise ErrorDominio("CONFLICTO_VERSION", "El perfil cambió; consulta la versión actual")
        if capitulo.status not in (Capitulo.Status.BORRADOR, Capitulo.Status.CON_OBSERVACIONES):
            raise ErrorDominio("CONFLICTO_VERSION", "El capítulo debe volver a borrador antes de editarse")
        secuencia = [paso for pasos in PASOS_CAPITULO.values() for paso in pasos]
        if codigo_paso != "P01":
            anterior = secuencia[secuencia.index(codigo_paso) - 1]
            if not ProgresoPaso.objects.filter(
                project=proyecto,
                step_code=anterior,
                status=ProgresoPaso.Status.COMPLETADO,
            ).exists():
                raise ErrorDominio("PRERREQUISITO_BLOQUEADO", f"Completa {anterior} antes de {codigo_paso}")
        ejecutar_materializador_paso(proyecto, perfil, codigo_paso, datos_validados)
        if capitulo.status == Capitulo.Status.CON_OBSERVACIONES:
            capitulo.reanudar_edicion()
            capitulo.save(update_fields=["status", "updated_at"])
        revision_anterior = capitulo.revisions.order_by("-revision_no").first()
        revision = RevisionCapitulo.objects.create(
            chapter=capitulo,
            revision_no=(revision_anterior.revision_no + 1 if revision_anterior else 1),
            step_code=codigo_paso,
            idempotency_key=clave,
            content_md=contenido_md,
            content_sha256=hashlib.sha256(contenido_md.encode("utf-8")).hexdigest(),
            created_by=usuario,
        )
        ProgresoPaso.objects.update_or_create(project=proyecto, step_code=codigo_paso, defaults={
            "status": ProgresoPaso.Status.COMPLETADO, "output_json": datos_validados, "completed_at": timezone.now(),
        })
        perfil.lock_version += 1
        perfil.save(update_fields=[
            "lock_version", "problem_statement", "ods_code",
            "unit_of_analysis", "place", "period_text", "approach", "updated_at",
        ])
        return {**_datos_revision(revision), "version_estado": perfil.lock_version, "idempotente": False}


def enviar_capitulo_servicio(usuario, id_proyecto, numero_capitulo: int) -> dict:
    proyecto = requerir_proyecto(usuario, id_proyecto, solo_tesista=True)
    if numero_capitulo not in PASOS_CAPITULO:
        raise ErrorDominio("NO_ENCONTRADO", "Capítulo no disponible en la plataforma")
    with transaction.atomic():
        capitulo = Capitulo.objects.select_for_update().filter(project=proyecto, number=numero_capitulo).first()
        if capitulo is None or capitulo.status != Capitulo.Status.BORRADOR:
            raise ErrorDominio("CONFLICTO_VERSION", "El capítulo no está listo para enviar")
        completados = set(ProgresoPaso.objects.filter(
            project=proyecto,
            step_code__in=PASOS_CAPITULO[numero_capitulo],
            status=ProgresoPaso.Status.COMPLETADO,
        ).values_list("step_code", flat=True))
        if completados != set(PASOS_CAPITULO[numero_capitulo]):
            raise ErrorDominio("PRERREQUISITO_BLOQUEADO", "Completa todos los pasos del capítulo")
        revision = capitulo.revisions.order_by("-revision_no").first()
        if revision is None:
            raise ErrorDominio("PRERREQUISITO_BLOQUEADO", "Guarda una revisión antes de enviarla")
        capitulo.enviar()
        capitulo.save(update_fields=["status", "updated_at"])
        EventoRevision.objects.create(
            chapter=capitulo,
            revision=revision,
            actor=usuario,
            action=EventoRevision.Action.ENVIAR,
        )
    return obtener_capitulo_servicio(usuario, id_proyecto, numero_capitulo)
