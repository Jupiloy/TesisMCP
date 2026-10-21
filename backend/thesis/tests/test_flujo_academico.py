from uuid import uuid4
import json
import asyncio

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client
from docx import Document

from thesis.models import Capitulo, RevisionCapitulo, ParticipanteProyecto, EventoRevision
from thesis.services.errores import ErrorDominio
from thesis.services.exportaciones import exportar_borrador_docx
from thesis.services.proyectos import crear_proyecto_servicio
from thesis.services.revisiones import agregar_comentario_servicio, asignar_asesor_servicio, decidir_capitulo_servicio, resolver_comentario_servicio
from thesis.services.pasos import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio


@pytest.fixture
def contexto(db):
    usuarios = get_user_model().objects
    tesista = usuarios.create_user(email="flow-owner@example.org", password="pass", display_name="Ana")
    asesora = usuarios.create_user(email="flow-advisor@example.org", password="pass", display_name="Asesora")
    externa = usuarios.create_user(email="flow-outsider@example.org", password="pass", display_name="Otra")
    proyecto = crear_proyecto_servicio(tesista, "Tesis")
    return tesista, asesora, externa, proyecto


def salidas():
    candidatos = [{"id": i, "titulo_tentativo": f"Tema candidato número {i}", "pros": ["Acceso"],
                   "contras": ["Tiempo"], "viabilidad_preliminar": "MEDIA"} for i in range(1, 6)]
    puntaje = {"acceso_a_datos": 4, "relevancia_profesional": 4, "brecha_conocimiento": 4,
             "recursos_disponibles": 4}
    matriz = [{"tema_id": i, "titulo": f"Tema candidato número {i}", "puntajes": puntaje,
               "puntaje_total": 16, "justificacion_eleccion": "Se dispone de datos y tiempo suficiente."}
              for i in range(1, 4)]
    introduccion = "\n\n".join(["palabra " * 90] * 3).strip()
    return [
        {"temas_propuestos": candidatos, "tema_preseleccionado_id": 1},
        {"matriz_comparativa": matriz, "tema_ganador_id": 1, "tema_ganador_titulo": matriz[0]["titulo"]},
        {"ods_principal_numero": 4, "ods_principal_nombre": "Educación de calidad",
         "meta_ods_especifica": "4.4", "argumento_alineacion": "El trabajo aborda acceso a formación y necesidades de una comunidad educativa concreta.",
         "linea_utp_vinculada": "Tecnología educativa"},
        {"titulo_oficial": "Uso de herramientas digitales en estudiantes de Piura durante 2026",
         "conteo_palabras": 10, "variables_confirmadas": ["herramientas digitales"],
         "unidad_analisis_confirmada": "estudiantes", "lugar_confirmado": "Piura", "periodo_confirmado": 2026},
        {"contenido_markdown": introduccion, "num_parrafos": 3, "palabras_totales": 270},
    ]


def test_exportacion_borrador_contiene_revision_y_exige_membresia(contexto):
    tesista, _, externa, proyecto = contexto
    guardar_paso_servicio(tesista, proyecto.id, "P01", "# Tema propio\nTexto redactado por el tesista.", salidas()[0], 0, str(uuid4()))
    documento = Document(exportar_borrador_docx(tesista, proyecto.id))
    assert round(documento.sections[0].left_margin.cm, 1) == 3.0
    assert documento.styles["Normal"].font.name == "Arial"
    contenido = "\n".join(parrafo.text for parrafo in documento.paragraphs)
    assert "Texto redactado por el tesista." in contenido
    assert "Capítulo 1" in contenido
    assert "Capítulo 2" not in contenido
    cliente = Client()
    cliente.force_login(tesista)
    respuesta = cliente.get(f"/api/v1/proyectos/{proyecto.id}/exportar/borrador.docx")
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    with pytest.raises(ErrorDominio) as denegado:
        exportar_borrador_docx(externa, proyecto.id)
    assert denegado.value.codigo == "NO_ENCONTRADO"
    cliente.force_login(externa)
    assert cliente.get(f"/api/v1/proyectos/{proyecto.id}/exportar/borrador.docx").status_code == 404


def test_revision_completa_capitulo_con_revisiones_inmutables(contexto):
    tesista, asesora, externa, proyecto = contexto
    asignar_asesor_servicio(tesista, proyecto.id, asesora.email)
    assert ParticipanteProyecto.objects.filter(project=proyecto, user=asesora, active=True).exists()
    with pytest.raises(ErrorDominio) as denegado:
        asignar_asesor_servicio(externa, proyecto.id, asesora.email)
    assert denegado.value.codigo == "NO_ENCONTRADO"

    for indice, salida in enumerate(salidas(), start=1):
        codigo = f"P{indice:02d}"
        resultado = guardar_paso_servicio(tesista, proyecto.id, codigo, f"Texto de capítulo en paso {codigo}", salida,
                           indice - 1, str(uuid4()))
        assert resultado["numero_revision"] == indice
    capitulo = obtener_capitulo_servicio(tesista, proyecto.id, 1)
    assert capitulo["revision_actual"]["codigo_paso"] == "P05"
    enviado = enviar_capitulo_servicio(tesista, proyecto.id, 1)
    assert enviado["estado"] == "EN_REVISION"
    with pytest.raises(ErrorDominio) as bloqueado:
        decidir_capitulo_servicio(asesora, proyecto.id, 1, "SOLICITAR_CAMBIOS")
    assert bloqueado.value.codigo == "ERROR_VALIDACION"
    revision = RevisionCapitulo.objects.get(chapter__project=proyecto, chapter__number=1, revision_no=5)
    comentario = agregar_comentario_servicio(asesora, proyecto.id, 1, 0, 5, "Texto", "Aclare la formulación del capítulo")
    assert comentario["id_revision"] == revision.pk
    with pytest.raises(ErrorDominio) as bloqueado:
        decidir_capitulo_servicio(asesora, proyecto.id, 1, "APROBAR")
    assert bloqueado.value.codigo == "OBSERVACIONES_ASESOR_SIN_RESOLVER"
    assert decidir_capitulo_servicio(asesora, proyecto.id, 1, "SOLICITAR_CAMBIOS")["estado"] == "CON_OBSERVACIONES"
    otra_revision = guardar_paso_servicio(tesista, proyecto.id, "P05", "Texto corregido del capítulo", salidas()[4],
                        5, str(uuid4()))
    assert otra_revision["numero_revision"] == 6
    assert obtener_capitulo_servicio(tesista, proyecto.id, 1)["estado"] == "BORRADOR"
    enviar_capitulo_servicio(tesista, proyecto.id, 1)
    assert decidir_capitulo_servicio(asesora, proyecto.id, 1, "APROBAR")["estado"] == "APROBADO"
    assert Capitulo.objects.get(project=proyecto, number=1).approved_revision_id == otra_revision["id_revision"]
    assert EventoRevision.objects.filter(chapter__project=proyecto).count() == 4
    assert resolver_comentario_servicio(asesora, proyecto.id, comentario["id_comentario"])["estado"] == "RESUELTA"


def test_contrato_e_idempotencia_y_limite_capitulo_3(contexto):
    tesista, _, _, proyecto = contexto
    invalida = salidas()[0]
    invalida["tema_preseleccionado_id"] = 9
    with pytest.raises(ErrorDominio) as error_dominio:
        guardar_paso_servicio(tesista, proyecto.id, "P01", "Texto", invalida, 0, str(uuid4()))
    assert error_dominio.value.codigo == "ERROR_ESQUEMA_VALIDACION"
    clave = str(uuid4())
    valida = salidas()[0]
    primera = guardar_paso_servicio(tesista, proyecto.id, "P01", "Texto", valida, 0, clave)
    segunda = guardar_paso_servicio(tesista, proyecto.id, "P01", "Texto", valida, 0, clave)
    assert primera["id_revision"] == segunda["id_revision"]
    assert segunda["idempotente"] is True
    with pytest.raises(ErrorDominio) as error_dominio:
        guardar_paso_servicio(tesista, proyecto.id, "P03", "Texto", salidas()[2], 1, str(uuid4()))
    assert error_dominio.value.codigo == "PRERREQUISITO_BLOQUEADO"
    with pytest.raises(ErrorDominio) as error_dominio:
        obtener_capitulo_servicio(tesista, proyecto.id, 4)
    assert error_dominio.value.codigo == "NO_ENCONTRADO"
    with pytest.raises(IntegrityError):
        Capitulo.objects.create(project=proyecto, number=4)


def test_api_y_mcp_exponen_flujo_capitulos_1_a_3(contexto):
    tesista, asesora, externa, proyecto = contexto
    cliente = Client()
    cliente.force_login(tesista)
    catalogo = cliente.get("/api/v1/metodologia/catalogo")
    assert catalogo.status_code == 200, catalogo.content
    assert [paso["codigo"] for paso in catalogo.json()] == [f"P{numero:02d}" for numero in range(1, 13)]
    assert catalogo.json()[0]["dependencias"] == []
    assert catalogo.json()[1]["dependencias"] == ["P01"]
    assert catalogo.json()[0]["esquema_salida"]["additionalProperties"] is False

    listado = cliente.get("/api/v1/proyectos")
    assert listado.status_code == 200, listado.content
    assert [elemento["id_proyecto"] for elemento in listado.json()] == [str(proyecto.id)]
    cliente.force_login(externa)
    assert cliente.get("/api/v1/proyectos").json() == []
    cliente.force_login(tesista)

    asignado = cliente.post(f"/api/v1/proyectos/{proyecto.id}/asesor",
                           data=json.dumps({"correo": asesora.email}), content_type="application/json")
    assert asignado.status_code == 200, asignado.content
    guardado = cliente.put(f"/api/v1/proyectos/{proyecto.id}/pasos/P01", data=json.dumps({
        "contenido_md": "Texto confirmado por Ana", "datos_salida": salidas()[0],
        "version_esperada": 0, "clave_idempotencia": str(uuid4()),
    }), content_type="application/json")
    assert guardado.status_code == 200, guardado.content
    recargado = cliente.get(f"/api/v1/proyectos/{proyecto.id}")
    assert recargado.status_code == 200, recargado.content
    assert recargado.json()["pasos"][0]["estado"] == "COMPLETADO"
    assert recargado.json()["pasos"][0]["contenido_md"] == "Texto confirmado por Ana"
    assert recargado.json()["pasos"][0]["datos_salida"] == salidas()[0]
    assert recargado.json()["pasos"][1]["estado"] == "DISPONIBLE"
    conflicto = cliente.put(f"/api/v1/proyectos/{proyecto.id}/pasos/P01", data=json.dumps({
        "contenido_md": "Edición basada en una versión obsoleta", "datos_salida": salidas()[0],
        "version_esperada": 0, "clave_idempotencia": str(uuid4()),
    }), content_type="application/json")
    assert conflicto.status_code == 409
    assert conflicto.json() == {
        "codigo": "CONFLICTO_VERSION",
        "mensaje": "El perfil cambió; consulta la versión actual",
        "detalle": "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual",
    }
    cliente.force_login(asesora)
    panel = cliente.get("/api/v1/asesor/panel")
    assert panel.status_code == 200, panel.content
    assert panel.json()[0]["id_proyecto"] == str(proyecto.id)
    assert [capitulo["numero_capitulo"] for capitulo in panel.json()[0]["capitulos"]] == [1, 2, 3]
    capitulo = cliente.get(f"/api/v1/proyectos/{proyecto.id}/capitulos/1")
    assert capitulo.json()["revision_actual"]["codigo_paso"] == "P01"

    from mcp_server.server import app
    nombres_herramientas = {herramienta.name for herramienta in asyncio.run(app.list_tools())}
    assert {"guardar_paso", "consultar_capitulo", "decidir_capitulo", "buscar_antecedentes_peru", "explorar_idea"} <= nombres_herramientas
