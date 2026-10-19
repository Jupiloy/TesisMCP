from uuid import uuid4
import json
import asyncio

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client
from docx import Document

from thesis.models import Capitulo, RevisionCapitulo, ParticipanteProyecto, EventoRevision
from thesis.services.errors import ErrorDominio
from thesis.services.exports import exportar_borrador_docx
from thesis.services.projects import crear_proyecto_servicio
from thesis.services.reviews import agregar_comentario_servicio, asignar_asesor_servicio, decidir_capitulo_servicio, resolver_comentario_servicio
from thesis.services.steps import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio


@pytest.fixture
def context(db):
    users = get_user_model().objects
    owner = users.create_user(email="flow-owner@example.org", password="pass", display_name="Ana")
    advisor = users.create_user(email="flow-advisor@example.org", password="pass", display_name="Asesora")
    outsider = users.create_user(email="flow-outsider@example.org", password="pass", display_name="Otra")
    project = crear_proyecto_servicio(owner, "Tesis")
    return owner, advisor, outsider, project


def outputs():
    candidates = [{"id": i, "titulo_tentativo": f"Tema candidato número {i}", "pros": ["Acceso"],
                   "contras": ["Tiempo"], "viabilidad_preliminar": "MEDIA"} for i in range(1, 6)]
    score = {"acceso_a_datos": 4, "relevancia_profesional": 4, "brecha_conocimiento": 4,
             "recursos_disponibles": 4}
    matrix = [{"tema_id": i, "titulo": f"Tema candidato número {i}", "puntajes": score,
               "puntaje_total": 16, "justificacion_eleccion": "Se dispone de datos y tiempo suficiente."}
              for i in range(1, 4)]
    introduction = "\n\n".join(["palabra " * 90] * 3).strip()
    return [
        {"temas_propuestos": candidates, "tema_preseleccionado_id": 1},
        {"matriz_comparativa": matrix, "tema_ganador_id": 1, "tema_ganador_titulo": matrix[0]["titulo"]},
        {"ods_principal_numero": 4, "ods_principal_nombre": "Educación de calidad",
         "meta_ods_especifica": "4.4", "argumento_alineacion": "El trabajo aborda acceso a formación y necesidades de una comunidad educativa concreta.",
         "linea_utp_vinculada": "Tecnología educativa"},
        {"titulo_oficial": "Uso de herramientas digitales en estudiantes de Piura durante 2026",
         "conteo_palabras": 10, "variables_confirmadas": ["herramientas digitales"],
         "unidad_analisis_confirmada": "estudiantes", "lugar_confirmado": "Piura", "periodo_confirmado": 2026},
        {"contenido_markdown": introduction, "num_parrafos": 3, "palabras_totales": 270},
    ]


def test_exportacion_borrador_contiene_revision_y_exige_membresia(context):
    owner, _, outsider, project = context
    guardar_paso_servicio(owner, project.id, "P01", "# Tema propio\nTexto redactado por el tesista.", outputs()[0], 0, str(uuid4()))
    document = Document(exportar_borrador_docx(owner, project.id))
    assert round(document.sections[0].left_margin.cm, 1) == 3.0
    assert document.styles["Normal"].font.name == "Arial"
    body = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Texto redactado por el tesista." in body
    assert "Capítulo 1" in body
    assert "Capítulo 2" not in body
    client = Client()
    client.force_login(owner)
    response = client.get(f"/api/v1/projects/{project.id}/export/draft.docx")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    with pytest.raises(ErrorDominio) as denied:
        exportar_borrador_docx(outsider, project.id)
    assert denied.value.code == "NOT_FOUND"
    client.force_login(outsider)
    assert client.get(f"/api/v1/projects/{project.id}/export/draft.docx").status_code == 404


def test_revision_completa_capitulo_con_revisiones_inmutables(context):
    owner, advisor, outsider, project = context
    asignar_asesor_servicio(owner, project.id, advisor.email)
    assert ParticipanteProyecto.objects.filter(project=project, user=advisor, active=True).exists()
    with pytest.raises(ErrorDominio) as denied:
        asignar_asesor_servicio(outsider, project.id, advisor.email)
    assert denied.value.code == "NOT_FOUND"

    for index, output in enumerate(outputs(), start=1):
        code = f"P{index:02d}"
        result = guardar_paso_servicio(owner, project.id, code, f"Texto de capítulo en paso {code}", output,
                           index - 1, str(uuid4()))
        assert result["revision_no"] == index
    chapter = obtener_capitulo_servicio(owner, project.id, 1)
    assert chapter["latest_revision"]["step_code"] == "P05"
    submitted = enviar_capitulo_servicio(owner, project.id, 1)
    assert submitted["status"] == "READY"
    with pytest.raises(ErrorDominio) as blocked:
        decidir_capitulo_servicio(advisor, project.id, 1, "REQUEST_CHANGES")
    assert blocked.value.code == "VALIDATION_ERROR"
    revision = RevisionCapitulo.objects.get(chapter__project=project, chapter__number=1, revision_no=5)
    comment = agregar_comentario_servicio(advisor, project.id, 1, 0, 5, "Texto", "Aclare la formulación del capítulo")
    assert comment["revision_id"] == revision.pk
    with pytest.raises(ErrorDominio) as blocked:
        decidir_capitulo_servicio(advisor, project.id, 1, "APPROVE")
    assert blocked.value.code == "ADVISOR_UNRESOLVED_COMMENTS"
    assert decidir_capitulo_servicio(advisor, project.id, 1, "REQUEST_CHANGES")["status"] == "CHANGES_REQUESTED"
    another = guardar_paso_servicio(owner, project.id, "P05", "Texto corregido del capítulo", outputs()[4],
                        5, str(uuid4()))
    assert another["revision_no"] == 6
    assert obtener_capitulo_servicio(owner, project.id, 1)["status"] == "DRAFT"
    enviar_capitulo_servicio(owner, project.id, 1)
    assert decidir_capitulo_servicio(advisor, project.id, 1, "APPROVE")["status"] == "APPROVED"
    assert Capitulo.objects.get(project=project, number=1).approved_revision_id == another["revision_id"]
    assert EventoRevision.objects.filter(chapter__project=project).count() == 4
    assert resolver_comentario_servicio(advisor, project.id, comment["comment_id"])["status"] == "RESOLVED"


def test_contrato_e_idempotencia_y_limite_capitulo_3(context):
    owner, _, _, project = context
    invalid = outputs()[0]
    invalid["tema_preseleccionado_id"] = 9
    with pytest.raises(ErrorDominio) as error:
        guardar_paso_servicio(owner, project.id, "P01", "Texto", invalid, 0, str(uuid4()))
    assert error.value.code == "VALIDATION_SCHEMA_ERROR"
    key = str(uuid4())
    valid = outputs()[0]
    first = guardar_paso_servicio(owner, project.id, "P01", "Texto", valid, 0, key)
    second = guardar_paso_servicio(owner, project.id, "P01", "Texto", valid, 0, key)
    assert first["revision_id"] == second["revision_id"]
    assert second["idempotent"] is True
    with pytest.raises(ErrorDominio) as error:
        guardar_paso_servicio(owner, project.id, "P03", "Texto", outputs()[2], 1, str(uuid4()))
    assert error.value.code == "PREREQUISITE_LOCKED"
    with pytest.raises(ErrorDominio) as error:
        obtener_capitulo_servicio(owner, project.id, 4)
    assert error.value.code == "NOT_FOUND"
    with pytest.raises(IntegrityError):
        Capitulo.objects.create(project=project, number=4)


def test_api_y_mcp_exponen_flujo_capitulos_1_a_3(context):
    owner, advisor, _, project = context
    client = Client()
    client.force_login(owner)
    assigned = client.post(f"/api/v1/projects/{project.id}/advisor",
                           data=json.dumps({"email": advisor.email}), content_type="application/json")
    assert assigned.status_code == 200, assigned.content
    saved = client.put(f"/api/v1/projects/{project.id}/steps/P01", data=json.dumps({
        "content_md": "Texto confirmado por Ana", "output_data": outputs()[0],
        "expected_version": 0, "idempotency_key": str(uuid4()),
    }), content_type="application/json")
    assert saved.status_code == 200, saved.content
    client.force_login(advisor)
    dashboard = client.get("/api/v1/projects/advisor/dashboard")
    assert dashboard.status_code == 200, dashboard.content
    assert dashboard.json()[0]["project_id"] == str(project.id)
    assert [c["chapter_no"] for c in dashboard.json()[0]["chapters"]] == [1, 2, 3]
    chapter = client.get(f"/api/v1/projects/{project.id}/chapters/1")
    assert chapter.json()["latest_revision"]["step_code"] == "P01"

    from mcp_server.server import app
    tool_names = {tool.name for tool in asyncio.run(app.list_tools())}
    assert {"guardar_paso", "consultar_capitulo", "decidir_capitulo", "buscar_antecedentes_peru", "explorar_idea"} <= tool_names
