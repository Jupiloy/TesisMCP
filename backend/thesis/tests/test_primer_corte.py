import json
import asyncio
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from thesis.integrations.openalex import buscar_trabajos_openalex
from thesis.services.errores import ErrorDominio
from thesis.services.exploracion import explorar_idea_servicio
from thesis.services.autenticacion_mcp import usuario_desde_token, emitir_token
from thesis.services.proyectos import crear_proyecto_servicio, obtener_estado_proyecto, registrar_idea_servicio


@pytest.fixture
def usuarios(db):
    modelo = get_user_model()
    return (
        modelo.objects.create_user(email="ana@example.org", password="strong-pass", display_name="Ana"),
        modelo.objects.create_user(email="otra@example.org", password="strong-pass", display_name="Otra"),
    )


def test_aislamiento_proyecto_y_conflicto_version(usuarios):
    ana, otra = usuarios
    proyecto = crear_proyecto_servicio(ana, "Tesis de Ana", "Título provisional")
    estado = registrar_idea_servicio(ana, proyecto.id, "Dificultades para usar herramientas digitales", 0)
    assert estado["idea_provisional"] == "Dificultades para usar herramientas digitales"
    assert estado["version_estado"] == 1
    with pytest.raises(ErrorDominio, match="Proyecto no encontrado"):
        obtener_estado_proyecto(otra, proyecto.id)
    with pytest.raises(ErrorDominio) as conflicto:
        registrar_idea_servicio(ana, proyecto.id, "Otra idea", 0)
    assert conflicto.value.codigo == "CONFLICTO_VERSION"
    assert obtener_estado_proyecto(ana, proyecto.id)["idea_provisional"] == estado["idea_provisional"]


def test_exploracion_marca_metadatos_y_maneja_idea_ausente(usuarios):
    ana, _ = usuarios
    proyecto = crear_proyecto_servicio(ana, "Tesis de Ana")
    assert proyecto.title == "Título por definir"
    assert explorar_idea_servicio(ana, proyecto.id)["estado_busqueda"] == "REQUIERE_IDEA"
    registrar_idea_servicio(ana, proyecto.id, "Uso de herramientas digitales en colegios", 0)
    consultas_observadas = []

    def busqueda_simulada(consulta):
        consultas_observadas.append(consulta)
        return [{"titulo": "Trabajo registrado", "nivel_verificacion": "SOLO_METADATOS", "texto_completo_inspeccionado": False}]

    resultado = explorar_idea_servicio(ana, proyecto.id, proveedor_busqueda=busqueda_simulada)
    assert consultas_observadas == ["Uso de herramientas digitales en colegios"]
    assert resultado["trabajos"][0]["texto_completo_inspeccionado"] is False


def test_token_mcp_vinculado_usuario_y_revocable(usuarios):
    ana, _ = usuarios
    token = emitir_token(ana)
    assert usuario_desde_token(token) == ana
    with pytest.raises(ErrorDominio) as error_dominio:
        usuario_desde_token("wrong-token")
    assert error_dominio.value.codigo == "NO_AUTENTICADO"
    from thesis.models import TokenAccesoMcp
    from django.utils import timezone

    TokenAccesoMcp.objects.update(revoked_at=timezone.now())
    with pytest.raises(ErrorDominio):
        usuario_desde_token(token)


def test_resultados_openalex_no_afirman_texto_completo():
    class Respuesta:
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

    with patch("thesis.integrations.openalex.urlopen", return_value=Respuesta()):
        trabajos = buscar_trabajos_openalex("idea provisional")
    assert trabajos[0]["nivel_verificacion"] == "SOLO_METADATOS"
    assert trabajos[0]["texto_completo_inspeccionado"] is False
    assert trabajos[0]["url_pdf"] == "https://example.org/file.pdf"


def test_api_requiere_sesion_y_csrf(usuarios):
    ana, _ = usuarios
    cliente = Client(enforce_csrf_checks=True)
    sin_autenticar = cliente.get("/api/v1/proyectos/00000000-0000-0000-0000-000000000000")
    assert sin_autenticar.status_code == 401
    assert sin_autenticar.json() == {
        "codigo": "NO_AUTENTICADO",
        "mensaje": "Se requiere una sesión autenticada",
        "detalle": "La solicitud no contiene una sesión válida",
    }
    assert cliente.get("/api/v1/sesion/actual").status_code == 401
    assert cliente.get("/api/v1/metodologia/catalogo").status_code == 401
    cliente.force_login(ana)
    sesion = cliente.get("/api/v1/sesion/actual")
    assert sesion.status_code == 200
    assert sesion.json() == {"correo": ana.email, "nombre_visible": "Ana"}
    assert "csrftoken" in cliente.cookies
    sin_csrf = cliente.post(
        "/api/v1/proyectos",
        data=json.dumps({"nombre": "Tesis", "titulo": "Provisional"}),
        content_type="application/json",
    )
    assert sin_csrf.status_code == 403
    assert set(sin_csrf.json()) == {"codigo", "mensaje", "detalle"}
    respuesta_documentacion = cliente.get("/api/v1/docs")
    assert respuesta_documentacion.status_code == 200
    esquema_abierto = cliente.get("/api/v1/openapi.json")
    assert esquema_abierto.status_code == 200
    rutas = set(esquema_abierto.json()["paths"])
    assert {
        "/api/v1/sesion/actual",
        "/api/v1/metodologia/catalogo",
        "/api/v1/proyectos",
        "/api/v1/proyectos/{id_proyecto}",
        "/api/v1/proyectos/{id_proyecto}/pasos/{codigo_paso}",
        "/api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}",
        "/api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/enviar",
        "/api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/comentarios",
        "/api/v1/asesor/panel",
    } <= rutas
    assert not any("/session/" in ruta or "/projects" in ruta or "/chapters" in ruta for ruta in rutas)
    token_csrf = cliente.cookies["csrftoken"].value
    entrada_invalida = cliente.post(
        "/api/v1/proyectos",
        data=json.dumps({"titulo": "Sin nombre"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token_csrf,
    )
    assert entrada_invalida.status_code == 422
    assert set(entrada_invalida.json()) == {"codigo", "mensaje", "detalle"}
    assert entrada_invalida.json()["codigo"] == "ERROR_VALIDACION"
    creado = cliente.post(
        "/api/v1/proyectos",
        data=json.dumps({"nombre": "Tesis", "titulo": "Provisional"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token_csrf,
    )
    assert creado.status_code == 200
    assert creado.json()["nombre"] == "Tesis"


@pytest.mark.django_db(transaction=True)
def test_mcp_usa_identidad_token_y_servicios_compartidos(monkeypatch):
    from mcp_server.server import app

    ana = get_user_model().objects.create_user(
        email="mcp-ana@example.org", password="strong-pass", display_name="Ana MCP",
    )
    monkeypatch.setenv("TESISMCP_MCP_TOKEN", emitir_token(ana))

    async def recorrido():
        creado = await app.call_tool("crear_proyecto", {"nombre": "Proyecto MCP", "titulo": "Título provisional"})
        id_proyecto = creado.structured_content["id_proyecto"]
        guardado = await app.call_tool("registrar_idea", {
            "id_proyecto": id_proyecto,
            "descripcion": "Dificultades de acceso a herramientas digitales",
            "version_esperada": 0,
        })
        estado = await app.call_tool("obtener_estado", {"id_proyecto": id_proyecto})
        return guardado.structured_content, estado.structured_content

    guardado, estado = asyncio.run(recorrido())
    assert guardado["version_estado"] == 1
    assert estado["idea_provisional"] == "Dificultades de acceso a herramientas digitales"


def test_error_publico_mcp_usa_contrato_canonico():
    from mcp.server.mcpserver.exceptions import ToolError
    from mcp_server.herramientas_proyecto import _uuid_proyecto

    with pytest.raises(ToolError) as error_herramienta:
        _uuid_proyecto("identificador-invalido")
    detalle = json.loads(str(error_herramienta.value))
    assert set(detalle) == {"codigo", "mensaje", "detalle"}
    assert detalle["codigo"] == "ERROR_VALIDACION"
