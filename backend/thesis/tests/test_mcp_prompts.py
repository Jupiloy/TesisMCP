"""Pruebas automatizadas para el Motor de Prompts y Roles del Servidor MCP (Capítulos 1 al 3: P01 a P12)."""

import asyncio
from unittest.mock import patch
from uuid import uuid4

import pytest

from mcp_server.server import app
from thesis.models import Usuario
from thesis.services.errors import ErrorDominio


def test_lista_prompts_contiene_12_pasos_y_roles():
    """Verifica que el catálogo de MCP exponga los 12 pasos metodológicos (Cap. 1-3) y los 3 roles."""
    async def run():
        prompts = await app.list_prompts()
        prompt_names = {p.name for p in prompts}

        assert len(prompts) == 15, f"Se esperaban 15 prompts registrados, se encontraron {len(prompts)}"

        for num in range(1, 13):
            code_str = f"p{num:02d}"
            matching = [name for name in prompt_names if f"paso_{code_str}" in name]
            assert len(matching) == 1, f"Falta el prompt del paso P{num:02d} en el catálogo MCP"

        assert "rol_asesor_metodologico" in prompt_names
        assert "rol_investigador_grounded" in prompt_names
        assert "rol_revisor_contratos" in prompt_names

    asyncio.run(run())


def test_ejemplos_prompts_validan_contratos_pasos():
    from mcp_server.prompts.templates import TEMPLATES_POR_PASO
    from thesis.services.step_contracts import CONTRATOS

    assert set(TEMPLATES_POR_PASO) == set(CONTRATOS)
    for code, template in TEMPLATES_POR_PASO.items():
        CONTRATOS[code].model_validate(template["esquema_json_ejemplo"])


def test_prompt_proyecto_requiere_usuario_autenticado():
    from mcp_server.prompts.hydration import hidratar_contexto_proyecto

    with patch("mcp_server.prompts.hydration.usuario_actual", side_effect=ErrorDominio(
        "UNAUTHENTICATED", "Token MCP inválido"
    )):
        with pytest.raises(ErrorDominio) as exc:
            hidratar_contexto_proyecto(str(uuid4()))
    assert exc.value.code == "UNAUTHENTICATED"


def test_obtener_prompt_sin_id_proyecto():
    """Verifica la generación de un prompt en modo preliminar sin ID de proyecto."""
    async def run():
        res = await app.get_prompt("paso_p01_mapa_temas", {})
        assert res is not None
        assert len(res.messages) == 1
        text = res.messages[0].content.text

        assert "P01: Mapa de Temas Viables" in text
        assert "Protocolo de Tres Roles Secuenciales" in text
        assert "Fase 1: Asesor Metodológico" in text
        assert "Fase 2: Investigador Grounded" in text
        assert "Fase 3: Revisor de Contratos" in text
        assert "No se especificó `project_id`" in text
        assert "temas_propuestos" in text

    asyncio.run(run())


@pytest.mark.django_db(transaction=True)
def test_obtener_prompt_con_proyecto_hidratado(monkeypatch):
    """Verifica que el prompt hidrate automáticamente los datos consolidados desde PostgreSQL."""
    from thesis.services.projects import crear_proyecto_servicio
    from thesis.services.mcp_auth import emitir_token

    student = Usuario.objects.create_user(
        email="tesista.prompts@utp.edu.pe",
        password="test-password-123",
        display_name="Tesista MCP Prompts",
    )
    monkeypatch.setenv("TESISMCP_MCP_TOKEN", emitir_token(student))
    project = crear_proyecto_servicio(student, "Proyecto MCP Test Prompts", "Sistema de Prueba para el Motor de Prompts")

    profile = project.profile
    profile.topic = "Arquitecturas Multi-Agente en Educación Superior"
    profile.ods_code = "ODS-04:4.4"
    profile.lock_version = 5
    profile.save()

    async def run():
        res = await app.get_prompt(
            "paso_p04_delimitacion_titulo",
            {"project_id": str(project.id), "detalle_estudiante": "Deseo enfocarlo en la UTP Sede Piura"}
        )
        assert res is not None
        text = res.messages[0].content.text

        assert str(project.id) in text
        assert "Sistema de Prueba para el Motor de Prompts" in text
        assert "Arquitecturas Multi-Agente en Educación Superior" in text
        assert "ODS-04:4.4" in text
        assert "lock_version" in text
        assert "`5`" in text
        assert "Deseo enfocarlo en la UTP Sede Piura" in text
        assert "titulo_oficial" in text

    asyncio.run(run())


def test_cargan_correctamente_prompts_12_pasos():
    """Comprueba que los 12 prompts de paso retornen contenido válido sin excepciones."""
    async def run():
        prompts = await app.list_prompts()
        step_prompts = [p for p in prompts if p.name.startswith("paso_p")]

        assert len(step_prompts) == 12

        for p in step_prompts:
            res = await app.get_prompt(p.name, {})
            assert res is not None
            assert len(res.messages) == 1
            content = res.messages[0].content.text
            assert len(content) > 200
            assert "Protocolo de Tres Roles Secuenciales" in content
            assert "guardar_paso" in content

    asyncio.run(run())


def test_prompts_roles_dedicados():
    """Comprueba el funcionamiento de los 3 prompts de rol."""
    async def run():
        res_adv = await app.get_prompt("rol_asesor_metodologico", {"consulta": "¿Cómo redacto mis hipótesis?"})
        text_adv = res_adv.messages[0].content.text
        assert "Modo Asesor Metodológico Principal" in text_adv
        assert "Taxonomía de Bloom" in text_adv
        assert "¿Cómo redacto mis hipótesis?" in text_adv

        res_inv = await app.get_prompt("rol_investigador_grounded", {"tema_o_criterio": "Model Context Protocol"})
        text_inv = res_inv.messages[0].content.text
        assert "Modo Investigador Grounded" in text_inv
        assert "buscar_antecedentes_peru" in text_inv
        assert "Model Context Protocol" in text_inv

        res_rev = await app.get_prompt("rol_revisor_contratos", {"paso_a_auditar": "P06"})
        text_rev = res_rev.messages[0].content.text
        assert "Modo Revisor de Contratos (Paso P06)" in text_rev
        assert "problema_central" in text_rev
        assert "pregunta_general" in text_rev

    asyncio.run(run())
