import json
import asyncio
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from thesis.integrations.openalex import buscar_trabajos_openalex
from thesis.services.errors import ErrorDominio
from thesis.services.exploration import explorar_idea_servicio
from thesis.services.mcp_auth import usuario_desde_token, emitir_token
from thesis.services.projects import crear_proyecto_servicio, obtener_estado_proyecto, registrar_idea_servicio


@pytest.fixture
def users(db):
    model = get_user_model()
    return (
        model.objects.create_user(email="ana@example.org", password="strong-pass", display_name="Ana"),
        model.objects.create_user(email="otra@example.org", password="strong-pass", display_name="Otra"),
    )


def test_aislamiento_proyecto_y_conflicto_version(users):
    ana, other = users
    project = crear_proyecto_servicio(ana, "Tesis de Ana", "Título provisional")
    state = registrar_idea_servicio(ana, project.id, "Dificultades para usar herramientas digitales", 0)
    assert state["idea_provisional"] == "Dificultades para usar herramientas digitales"
    assert state["state_version"] == 1
    with pytest.raises(ErrorDominio, match="Proyecto no encontrado"):
        obtener_estado_proyecto(other, project.id)
    with pytest.raises(ErrorDominio) as conflict:
        registrar_idea_servicio(ana, project.id, "Otra idea", 0)
    assert conflict.value.code == "VERSION_CONFLICT"
    assert obtener_estado_proyecto(ana, project.id)["idea_provisional"] == state["idea_provisional"]


def test_exploracion_marca_metadatos_y_maneja_idea_ausente(users):
    ana, _ = users
    project = crear_proyecto_servicio(ana, "Tesis de Ana")
    assert project.title == "Título por definir"
    assert explorar_idea_servicio(ana, project.id)["search_status"] == "NEEDS_IDEA"
    registrar_idea_servicio(ana, project.id, "Uso de herramientas digitales en colegios", 0)
    observed = []

    def fake_search(query):
        observed.append(query)
        return [{"title": "Trabajo registrado", "verification_level": "METADATA_ONLY", "full_text_inspected": False}]

    result = explorar_idea_servicio(ana, project.id, search_provider=fake_search)
    assert observed == ["Uso de herramientas digitales en colegios"]
    assert result["works"][0]["full_text_inspected"] is False


def test_token_mcp_vinculado_usuario_y_revocable(users):
    ana, _ = users
    token = emitir_token(ana)
    assert usuario_desde_token(token) == ana
    with pytest.raises(ErrorDominio) as error:
        usuario_desde_token("wrong-token")
    assert error.value.code == "UNAUTHENTICATED"
    from thesis.models import TokenAccesoMcp
    from django.utils import timezone

    TokenAccesoMcp.objects.update(revoked_at=timezone.now())
    with pytest.raises(ErrorDominio):
        usuario_desde_token(token)


def test_resultados_openalex_no_afirman_texto_completo():
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return json.dumps({"results": [{
                "id": "https://openalex.org/Wexample",
                "title": "Ejemplo de metadatos",
                "authorships": [{"author": {"display_name": "Persona"}}],
                "publication_year": None,
                "best_oa_location": {"pdf_url": "https://example.org/file.pdf"},
            }]}).encode()

    with patch("thesis.integrations.openalex.urlopen", return_value=Response()):
        works = buscar_trabajos_openalex("idea provisional")
    assert works[0]["verification_level"] == "METADATA_ONLY"
    assert works[0]["full_text_inspected"] is False
    assert works[0]["pdf_url"] == "https://example.org/file.pdf"


def test_api_requiere_sesion_y_csrf(users):
    ana, _ = users
    client = Client(enforce_csrf_checks=True)
    unauthenticated = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    assert unauthenticated.status_code == 401
    client.force_login(ana)
    missing_csrf = client.post("/api/v1/projects", data=json.dumps({"name": "Tesis", "title": "Provisional"}), content_type="application/json")
    assert missing_csrf.status_code == 403
    docs_response = client.get("/api/v1/docs")
    assert docs_response.status_code == 200
    csrf_token = client.cookies["csrftoken"].value
    created = client.post(
        "/api/v1/projects",
        data=json.dumps({"name": "Tesis", "title": "Provisional"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert created.status_code == 200
    assert created.json()["name"] == "Tesis"


@pytest.mark.django_db(transaction=True)
def test_mcp_usa_identidad_token_y_servicios_compartidos(monkeypatch):
    from mcp_server.server import app

    ana = get_user_model().objects.create_user(
        email="mcp-ana@example.org", password="strong-pass", display_name="Ana MCP",
    )
    monkeypatch.setenv("TESISMCP_MCP_TOKEN", emitir_token(ana))

    async def journey():
        created = await app.call_tool("crear_proyecto", {"name": "Proyecto MCP", "title": "Título provisional"})
        project_id = created.structured_content["project_id"]
        saved = await app.call_tool("registrar_idea", {
            "project_id": project_id,
            "description": "Dificultades de acceso a herramientas digitales",
            "expected_version": 0,
        })
        state = await app.call_tool("obtener_estado", {"project_id": project_id})
        return saved.structured_content, state.structured_content

    saved, state = asyncio.run(journey())
    assert saved["state_version"] == 1
    assert state["idea_provisional"] == "Dificultades de acceso a herramientas digitales"
