"""Simulación End-to-End del servidor MCP para el Avance de Capítulos 1 al 3 (P01 a P12)."""

import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp_server.server import app
from mcp_server.demo.case_data import _construir_payloads_12_pasos
from mcp_server.demo.support import (
    _inspeccionar_bd_relacional,
    _preparar_usuarios_y_tokens,
)


def _desenvolver(tool_res):
    sc = tool_res.structured_content
    if isinstance(sc, dict) and "result" in sc and len(sc) == 1:
        return sc["result"]
    return sc


async def probar_servidor_mcp():
    print("=" * 80)
    print("🚀 SIMULACIÓN END-TO-END DEL SERVIDOR MCP: AVANCE CAPÍTULOS 1 AL 3 (P01 -> P12)")
    print("⚠️ Los datos metodológicos son simulados para demostrar el flujo de los primeros 3 capítulos.")
    print("=" * 80)

    # 1. Catálogo de herramientas MCP
    tools = await app.list_tools()
    print(f"\n📦 1. Herramientas MCP registradas ({len(tools)} tools activas):")
    for tool in tools:
        print(f"   • {tool.name}: {tool.description.strip().splitlines()[0]}")

    res_estado = await app.call_tool("estado_servidor", {})
    info_srv = _desenvolver(res_estado)
    print(
        f"\n🩺 Estado del Servidor MCP: {info_srv['estado']} | "
        f"Capítulos disponibles: {info_srv['capitulos_disponibles']} | "
        f"Pasos registrados: {info_srv['total_pasos']} | "
        f"Prompts activos: {info_srv.get('total_prompts', 15)}"
    )

    prompts = await app.list_prompts()
    print(f"\n🧠 Prompts con roles secuenciales ({len(prompts)} prompts registrados):")
    print(f"   • Pasos Metodológicos (P01 a P12): {len([p for p in prompts if p.name.startswith('paso_')])}")
    print(f"   • Roles de Agente Dedicados      : {len([p for p in prompts if p.name.startswith('rol_')])}")
    for r in [p for p in prompts if p.name.startswith("rol_")]:
        print(f"     -> {r.name}: {r.description}")

    # 2. Preparar actores y tokens criptográficos
    student_email, advisor_email, student_token, advisor_token = await _preparar_usuarios_y_tokens()
    os.environ["TESISMCP_MCP_TOKEN"] = student_token
    print("\n🔐 2. Identidad MCP autenticada por token criptográfico:")
    print(f"   • Tesista: {student_email}")
    print(f"   • Asesor : {advisor_email}")

    # 3. Crear el proyecto y asignar al asesor mediante herramientas MCP
    res_proj = await app.call_tool(
        "crear_proyecto",
        {
            "name": "TesisMCP - Avance Capítulos 1 al 3 UTP Piura",
            "title": "Borrador Inicial TesisMCP",
        },
    )
    proj_state = _desenvolver(res_proj)
    project_id = proj_state["project_id"]
    expected_version = proj_state["state_version"]
    print(f"\n📁 3. Proyecto creado vía MCP `crear_proyecto`: ID = {project_id}")

    res_adv = await app.call_tool(
        "asignar_asesor",
        {"project_id": project_id, "email": advisor_email},
    )
    adv_data = _desenvolver(res_adv)
    print(f"   • Asesor asignado vía MCP `asignar_asesor`: {adv_data.get('advisor_email', advisor_email)}")

    # Demostración del Motor de Prompts: obtención de prompt hidratado con el proyecto
    p01_prompt = await app.get_prompt("paso_p01_mapa_temas", {"project_id": project_id})
    print("\n   ⚡ Demostración de Prompt Hidratado: `paso_p01_mapa_temas`")
    print(f"      Título Prompt: {p01_prompt.description}")
    preview_line = [l for l in p01_prompt.messages[0].content.text.splitlines() if "ID del Proyecto" in l]
    if preview_line:
        print(f"      Contexto BD Inyectado: {preview_line[0].strip()}")

    # 4. Recorrer los 12 pasos metodológicos (Capítulos 1 al 3) vía `guardar_paso`
    payloads = _construir_payloads_12_pasos()
    print("\n" + "-" * 80)
    print("🧭 4. EJECUTANDO LOS 12 PASOS METODOLÓGICOS (P01 -> P12) VÍA MCP `guardar_paso`")
    print("-" * 80)

    for step_num in range(1, 13):
        step_code = f"P{step_num:02d}"
        content_md, output_data = payloads[step_code]

        res_step = await app.call_tool(
            "guardar_paso",
            {
                "project_id": project_id,
                "step_code": step_code,
                "content_md": content_md,
                "output_data": output_data,
                "expected_version": expected_version,
                "idempotency_key": str(uuid4()),
            },
        )
        step_result = _desenvolver(res_step)
        expected_version = step_result["state_version"]
        print(
            f"   ✓ [{step_code}] Cap. {step_result['chapter_no']} guardado | "
            f"Rev #{step_result['revision_no']} | lock_version={expected_version}"
        )

    # Comprobar que el servidor rechaza pasos fuera del alcance de los Capítulos 1 al 3 (p. ej. P13)
    try:
        await app.call_tool(
            "guardar_paso",
            {
                "project_id": project_id,
                "step_code": "P13",
                "content_md": "# Intento de guardar Capítulo 4",
                "output_data": {},
                "expected_version": expected_version,
                "idempotency_key": str(uuid4()),
            },
        )
    except Exception as exc:
        print(f"\n   🛡️ Guardia de alcance activada al intentar ejecutar P13 (Cap. 4): {exc}")

    # 5. Ciclo colaborativo Tesista <-> Asesor en los Capítulos 1 al 3
    print("\n" + "-" * 80)
    print("👨‍🏫 5. CICLO DE REVISIÓN DOCENTE E INMUTABILIDAD (CAPÍTULOS 1 AL 3)")
    print("-" * 80)

    os.environ["TESISMCP_MCP_TOKEN"] = student_token
    for ch_no in range(1, 4):
        res_sub = await app.call_tool("enviar_capitulo", {"project_id": project_id, "chapter_no": ch_no})
        sub_data = _desenvolver(res_sub)
        print(f"   📤 Tesista envió Capítulo {ch_no} -> estado: {sub_data['status']}")

    os.environ["TESISMCP_MCP_TOKEN"] = advisor_token
    res_cap3 = await app.call_tool("consultar_capitulo", {"project_id": project_id, "chapter_no": 3})
    cap3_data = _desenvolver(res_cap3)
    texto_cap3 = cap3_data["latest_revision"]["content_md"]
    fragmento = "Matriz de Operacionalización"
    start_cp = texto_cap3.index(fragmento)
    end_cp = start_cp + len(fragmento)

    res_obs = await app.call_tool(
        "observar_fragmento",
        {
            "project_id": project_id,
            "chapter_no": 3,
            "start_cp": start_cp,
            "end_cp": end_cp,
            "selected_text": fragmento,
            "body": "Excelente operacionalización del Protocolo MCP; verificar que los indicadores mantengan escala ordinal.",
        },
    )
    obs_data = _desenvolver(res_obs)
    comment_id = obs_data["comment_id"]
    print(f"\n   📌 Asesor registró observación anclada #{comment_id} en Cap. 3 sobre '{fragmento}' (pos {start_cp}..{end_cp})")

    try:
        await app.call_tool(
            "decidir_capitulo",
            {
                "project_id": project_id,
                "chapter_no": 3,
                "action": "APPROVE",
                "reason": "Intento de aprobar con observación abierta",
            },
        )
    except Exception as exc:
        print(f"   🛡️ Guardia de dominio activada al intentar aprobar con observación abierta: {exc}")

    await app.call_tool("resolver_observacion", {"project_id": project_id, "comment_id": comment_id})
    print(f"   ✅ Asesor marcó como RESUELTA la observación #{comment_id}")

    for ch_no in range(1, 4):
        res_dec = await app.call_tool(
            "decidir_capitulo",
            {
                "project_id": project_id,
                "chapter_no": ch_no,
                "action": "APPROVE",
                "reason": f"Capítulo {ch_no} verificado metodológicamente y aprobado sin observaciones pendientes.",
            },
        )
        dec_data = _desenvolver(res_dec)
        print(f"   🏆 Asesor aprobó Capítulo {ch_no} -> estado final: {dec_data['status']}")

    # 6. Inspección final del estado relacional en PostgreSQL
    res_final_state = await app.call_tool("obtener_estado", {"project_id": project_id})
    final_state = _desenvolver(res_final_state)
    db_metrics = await _inspeccionar_bd_relacional(project_id)

    print("\n" + "=" * 80)
    print("📊 6. RESUMEN DE ENTIDADES CANÓNICAS MATERIALIZADAS EN POSTGRESQL")
    print("=" * 80)
    print(f"   • Título Oficial (P04)         : {final_state['title']}")
    print(f"   • Código ODS (P03)             : {db_metrics['ods_code']}")
    print(f"   • Versión de Estado (Optimistic): lock_version = {db_metrics['lock_version']}")
    print(f"   • Pasos Completados            : {db_metrics['steps_completed']} / 12")
    print(f"   • Capítulos Aprobados          : {db_metrics['chapters_approved']} / 3")
    print(f"   • Revisiones Inmutables        : {db_metrics['chapter_revisions']}")
    print(f"   • Filas Matriz de Consistencia : {db_metrics['consistency_rows']} (1 General + 3 Específicas)")
    print(f"   • Variables Relacionales (P11) : {db_metrics['research_variables']} (VI + VD)")
    print(f"   • Cruces Fila x Variable       : {db_metrics['consistency_row_vars']}")
    print(f"   • Dimensiones Operacionales    : {db_metrics['variable_dimensions']}")
    print(f"   • Indicadores Medibles (P12)   : {db_metrics['indicators']}")
    print(f"   • Observaciones Resueltas      : {db_metrics['review_comments_resolved']}")
    print(f"   • Eventos de Auditoría Docente : {db_metrics['review_events']}")
    print("=" * 80)
    print("✅ SIMULACIÓN DE AVANCE (CAPÍTULOS 1 AL 3) COMPLETADA AL 100% SIN ERRORES.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(probar_servidor_mcp())
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
