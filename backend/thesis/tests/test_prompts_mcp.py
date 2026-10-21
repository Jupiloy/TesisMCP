"""Pruebas automatizadas para el Motor de Prompts y Roles del Servidor MCP (Capítulos 1 al 3: P01 a P12)."""

import asyncio
from unittest.mock import patch
from uuid import uuid4

import pytest

from mcp_server.server import app
from thesis.models import Usuario
from thesis.services.errores import ErrorDominio


def test_lista_prompts_contiene_12_pasos_y_roles():
    """Verifica que el catálogo de MCP exponga los 12 pasos metodológicos (Cap. 1-3) y los 3 roles."""
    async def ejecutar():
        prompts = await app.list_prompts()
        nombres_prompts = {prompt.name for prompt in prompts}

        assert len(prompts) == 15, f"Se esperaban 15 prompts registrados, se encontraron {len(prompts)}"

        for numero in range(1, 13):
            codigo = f"p{numero:02d}"
            coincidencias = [nombre for nombre in nombres_prompts if f"paso_{codigo}" in nombre]
            assert len(coincidencias) == 1, f"Falta el prompt del paso P{numero:02d} en el catálogo MCP"

        assert "rol_asesor_metodologico" in nombres_prompts
        assert "rol_investigador_grounded" in nombres_prompts
        assert "rol_revisor_contratos" in nombres_prompts

    asyncio.run(ejecutar())


def test_ejemplos_prompts_validan_contratos_pasos():
    from mcp_server.prompts.plantillas import PLANTILLAS_POR_PASO
    from thesis.services.contratos_pasos import CONTRATOS

    assert set(PLANTILLAS_POR_PASO) == set(CONTRATOS)
    for codigo, plantilla in PLANTILLAS_POR_PASO.items():
        CONTRATOS[codigo].model_validate(plantilla["esquema_json_ejemplo"])


def test_prompt_proyecto_requiere_usuario_autenticado():
    from mcp_server.prompts.hidratacion import hidratar_contexto_proyecto

    with patch("mcp_server.prompts.hidratacion.usuario_actual", side_effect=ErrorDominio(
        "NO_AUTENTICADO", "Token MCP inválido"
    )):
        with pytest.raises(ErrorDominio) as error:
            hidratar_contexto_proyecto(str(uuid4()))
    assert error.value.codigo == "NO_AUTENTICADO"


def test_obtener_prompt_sin_id_proyecto():
    """Verifica la generación de un prompt en modo preliminar sin ID de proyecto."""
    async def ejecutar():
        respuesta = await app.get_prompt("paso_p01_mapa_temas", {})
        assert respuesta is not None
        assert len(respuesta.messages) == 1
        texto = respuesta.messages[0].content.text

        assert "P01: Mapa de Temas Viables" in texto
        assert "Protocolo de Tres Roles Secuenciales" in texto
        assert "Fase 1: Asesor Metodológico" in texto
        assert "Fase 2: Investigador Grounded" in texto
        assert "Fase 3: Revisor de Contratos" in texto
        assert "No se especificó `id_proyecto`" in texto
        assert "temas_propuestos" in texto

    asyncio.run(ejecutar())


@pytest.mark.django_db(transaction=True)
def test_obtener_prompt_con_proyecto_hidratado(monkeypatch):
    """Verifica que el prompt hidrate automáticamente los datos consolidados desde PostgreSQL."""
    from thesis.services.proyectos import crear_proyecto_servicio
    from thesis.services.autenticacion_mcp import emitir_token

    tesista = Usuario.objects.create_user(
        email="tesista.prompts@utp.edu.pe",
        password="test-password-123",
        display_name="Tesista MCP Prompts",
    )
    monkeypatch.setenv("TESISMCP_MCP_TOKEN", emitir_token(tesista))
    proyecto = crear_proyecto_servicio(tesista, "Proyecto MCP Test Prompts", "Sistema de Prueba para el Motor de Prompts")

    perfil = proyecto.profile
    perfil.topic = "Arquitecturas Multi-Agente en Educación Superior"
    perfil.ods_code = "ODS-04:4.4"
    perfil.lock_version = 5
    perfil.save()

    async def ejecutar():
        respuesta = await app.get_prompt(
            "paso_p04_delimitacion_titulo",
            {"id_proyecto": str(proyecto.id), "detalle_estudiante": "Deseo enfocarlo en la UTP Sede Piura"}
        )
        assert respuesta is not None
        texto = respuesta.messages[0].content.text

        assert str(proyecto.id) in texto
        assert "Sistema de Prueba para el Motor de Prompts" in texto
        assert "Arquitecturas Multi-Agente en Educación Superior" in texto
        assert "ODS-04:4.4" in texto
        assert "version_estado" in texto
        assert "`5`" in texto
        assert "Deseo enfocarlo en la UTP Sede Piura" in texto
        assert "titulo_oficial" in texto

    asyncio.run(ejecutar())


def test_cargan_correctamente_prompts_12_pasos():
    """Comprueba que los 12 prompts de paso retornen contenido válido sin excepciones."""
    async def ejecutar():
        prompts = await app.list_prompts()
        prompts_pasos = [prompt for prompt in prompts if prompt.name.startswith("paso_p")]

        assert len(prompts_pasos) == 12

        for prompt in prompts_pasos:
            respuesta = await app.get_prompt(prompt.name, {})
            assert respuesta is not None
            assert len(respuesta.messages) == 1
            contenido = respuesta.messages[0].content.text
            assert len(contenido) > 200
            assert "Protocolo de Tres Roles Secuenciales" in contenido
            assert "guardar_paso" in contenido

    asyncio.run(ejecutar())


def test_prompts_roles_dedicados():
    """Comprueba el funcionamiento de los 3 prompts de rol."""
    async def ejecutar():
        respuesta_asesor = await app.get_prompt("rol_asesor_metodologico", {"consulta": "¿Cómo redacto mis hipótesis?"})
        texto_asesor = respuesta_asesor.messages[0].content.text
        assert "Modo Asesor Metodológico Principal" in texto_asesor
        assert "Taxonomía de Bloom" in texto_asesor
        assert "¿Cómo redacto mis hipótesis?" in texto_asesor

        respuesta_investigador = await app.get_prompt("rol_investigador_grounded", {"tema_o_criterio": "Model Context Protocol"})
        texto_investigador = respuesta_investigador.messages[0].content.text
        assert "Modo Investigador Grounded" in texto_investigador
        assert "buscar_antecedentes_peru" in texto_investigador
        assert "Model Context Protocol" in texto_investigador

        respuesta_revisor = await app.get_prompt("rol_revisor_contratos", {"paso_a_auditar": "P06"})
        texto_revisor = respuesta_revisor.messages[0].content.text
        assert "Modo Revisor de Contratos (Paso P06)" in texto_revisor
        assert "problema_central" in texto_revisor
        assert "pregunta_general" in texto_revisor

    asyncio.run(ejecutar())
