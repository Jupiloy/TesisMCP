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
from mcp_server.demostracion.datos_caso import _construir_cargas_12_pasos
from mcp_server.demostracion.soporte import (
    _inspeccionar_bd_relacional,
    _preparar_usuarios_y_tokens,
)


def _desenvolver(resultado_herramienta):
    contenido_estructurado = resultado_herramienta.structured_content
    if (
        isinstance(contenido_estructurado, dict)
        and "result" in contenido_estructurado
        and len(contenido_estructurado) == 1
    ):
        return contenido_estructurado["result"]
    return contenido_estructurado


async def probar_servidor_mcp():
    print("=" * 80)
    print("🚀 SIMULACIÓN END-TO-END DEL SERVIDOR MCP: AVANCE CAPÍTULOS 1 AL 3 (P01 -> P12)")
    print("⚠️ Los datos metodológicos son simulados para demostrar el flujo de los primeros 3 capítulos.")
    print("=" * 80)

    # 1. Catálogo de herramientas MCP
    herramientas = await app.list_tools()
    print(f"\n📦 1. Herramientas MCP registradas ({len(herramientas)} activas):")
    for herramienta in herramientas:
        print(f"   • {herramienta.name}: {herramienta.description.strip().splitlines()[0]}")

    resultado_estado = await app.call_tool("estado_servidor", {})
    informacion_servidor = _desenvolver(resultado_estado)
    print(
        f"\n🩺 Estado del Servidor MCP: {informacion_servidor['estado']} | "
        f"Capítulos disponibles: {informacion_servidor['capitulos_disponibles']} | "
        f"Pasos registrados: {informacion_servidor['total_pasos']} | "
        f"Prompts activos: {informacion_servidor.get('total_prompts', 15)}"
    )

    prompts = await app.list_prompts()
    print(f"\n🧠 Prompts con roles secuenciales ({len(prompts)} prompts registrados):")
    print(f"   • Pasos Metodológicos (P01 a P12): {len([p for p in prompts if p.name.startswith('paso_')])}")
    print(f"   • Roles de Agente Dedicados      : {len([p for p in prompts if p.name.startswith('rol_')])}")
    for r in [p for p in prompts if p.name.startswith("rol_")]:
        print(f"     -> {r.name}: {r.description}")

    # 2. Preparar actores y tokens criptográficos
    correo_tesista, correo_asesor, token_tesista, token_asesor = await _preparar_usuarios_y_tokens()
    os.environ["TESISMCP_MCP_TOKEN"] = token_tesista
    print("\n🔐 2. Identidad MCP autenticada por token criptográfico:")
    print(f"   • Tesista: {correo_tesista}")
    print(f"   • Asesor : {correo_asesor}")

    # 3. Crear el proyecto y asignar al asesor mediante herramientas MCP
    resultado_proyecto = await app.call_tool(
        "crear_proyecto",
        {
            "nombre": "TesisMCP - Avance Capítulos 1 al 3 UTP Piura",
            "titulo": "Borrador Inicial TesisMCP",
        },
    )
    estado_proyecto = _desenvolver(resultado_proyecto)
    id_proyecto = estado_proyecto["id_proyecto"]
    version_esperada = estado_proyecto["version_estado"]
    print(f"\n📁 3. Proyecto creado vía MCP `crear_proyecto`: ID = {id_proyecto}")

    resultado_asesor = await app.call_tool(
        "asignar_asesor",
        {"id_proyecto": id_proyecto, "correo": correo_asesor},
    )
    datos_asesor = _desenvolver(resultado_asesor)
    print(f"   • Asesor asignado vía MCP `asignar_asesor`: {datos_asesor.get('correo_asesor', correo_asesor)}")

    # Demostración del Motor de Prompts: obtención de prompt hidratado con el proyecto
    prompt_p01 = await app.get_prompt("paso_p01_mapa_temas", {"id_proyecto": id_proyecto})
    print("\n   ⚡ Demostración de Prompt Hidratado: `paso_p01_mapa_temas`")
    print(f"      Título Prompt: {prompt_p01.description}")
    lineas_vista_previa = [
        linea for linea in prompt_p01.messages[0].content.text.splitlines()
        if "ID del Proyecto" in linea
    ]
    if lineas_vista_previa:
        print(f"      Contexto BD Inyectado: {lineas_vista_previa[0].strip()}")

    # 4. Recorrer los 12 pasos metodológicos (Capítulos 1 al 3) vía `guardar_paso`
    cargas = _construir_cargas_12_pasos()
    print("\n" + "-" * 80)
    print("🧭 4. EJECUTANDO LOS 12 PASOS METODOLÓGICOS (P01 -> P12) VÍA MCP `guardar_paso`")
    print("-" * 80)

    for numero_paso in range(1, 13):
        codigo_paso = f"P{numero_paso:02d}"
        contenido_md, datos_salida = cargas[codigo_paso]

        resultado_paso = await app.call_tool(
            "guardar_paso",
            {
                "id_proyecto": id_proyecto,
                "codigo_paso": codigo_paso,
                "contenido_md": contenido_md,
                "datos_salida": datos_salida,
                "version_esperada": version_esperada,
                "clave_idempotencia": str(uuid4()),
            },
        )
        resultado_guardado = _desenvolver(resultado_paso)
        version_esperada = resultado_guardado["version_estado"]
        print(
            f"   ✓ [{codigo_paso}] Cap. {resultado_guardado['numero_capitulo']} guardado | "
            f"Rev #{resultado_guardado['numero_revision']} | version_estado={version_esperada}"
        )

    # Comprobar que el servidor rechaza pasos fuera del alcance de los Capítulos 1 al 3 (p. ej. P13)
    try:
        await app.call_tool(
            "guardar_paso",
            {
                "id_proyecto": id_proyecto,
                "codigo_paso": "P13",
                "contenido_md": "# Intento de guardar Capítulo 4",
                "datos_salida": {},
                "version_esperada": version_esperada,
                "clave_idempotencia": str(uuid4()),
            },
        )
    except Exception as exc:
        print(f"\n   🛡️ Guardia de alcance activada al intentar ejecutar P13 (Cap. 4): {exc}")

    # 5. Ciclo colaborativo Tesista <-> Asesor en los Capítulos 1 al 3
    print("\n" + "-" * 80)
    print("👨‍🏫 5. CICLO DE REVISIÓN DOCENTE E INMUTABILIDAD (CAPÍTULOS 1 AL 3)")
    print("-" * 80)

    os.environ["TESISMCP_MCP_TOKEN"] = token_tesista
    for numero_capitulo in range(1, 4):
        resultado_envio = await app.call_tool(
            "enviar_capitulo",
            {"id_proyecto": id_proyecto, "numero_capitulo": numero_capitulo},
        )
        datos_envio = _desenvolver(resultado_envio)
        print(f"   📤 Tesista envió Capítulo {numero_capitulo} -> estado: {datos_envio['estado']}")

    os.environ["TESISMCP_MCP_TOKEN"] = token_asesor
    resultado_capitulo_3 = await app.call_tool(
        "consultar_capitulo", {"id_proyecto": id_proyecto, "numero_capitulo": 3}
    )
    datos_capitulo_3 = _desenvolver(resultado_capitulo_3)
    texto_cap3 = datos_capitulo_3["revision_actual"]["contenido_md"]
    fragmento = "Matriz de Operacionalización"
    inicio_caracter = texto_cap3.index(fragmento)
    fin_caracter = inicio_caracter + len(fragmento)

    resultado_observacion = await app.call_tool(
        "observar_fragmento",
        {
            "id_proyecto": id_proyecto,
            "numero_capitulo": 3,
            "inicio_caracter": inicio_caracter,
            "fin_caracter": fin_caracter,
            "texto_seleccionado": fragmento,
            "contenido": "Excelente operacionalización del Protocolo MCP; verificar que los indicadores mantengan escala ordinal.",
        },
    )
    datos_observacion = _desenvolver(resultado_observacion)
    id_comentario = datos_observacion["id_comentario"]
    print(
        f"\n   📌 Asesor registró observación anclada #{id_comentario} en Cap. 3 "
        f"sobre '{fragmento}' (pos {inicio_caracter}..{fin_caracter})"
    )

    try:
        await app.call_tool(
            "decidir_capitulo",
            {
                "id_proyecto": id_proyecto,
                "numero_capitulo": 3,
                "accion": "APROBAR",
                "motivo": "Intento de aprobar con observación abierta",
            },
        )
    except Exception as exc:
        print(f"   🛡️ Guardia de dominio activada al intentar aprobar con observación abierta: {exc}")

    await app.call_tool("resolver_observacion", {"id_proyecto": id_proyecto, "id_comentario": id_comentario})
    print(f"   ✅ Asesor marcó como RESUELTA la observación #{id_comentario}")

    for numero_capitulo in range(1, 4):
        resultado_decision = await app.call_tool(
            "decidir_capitulo",
            {
                "id_proyecto": id_proyecto,
                "numero_capitulo": numero_capitulo,
                "accion": "APROBAR",
                "motivo": f"Capítulo {numero_capitulo} verificado metodológicamente y aprobado sin observaciones pendientes.",
            },
        )
        datos_decision = _desenvolver(resultado_decision)
        print(f"   🏆 Asesor aprobó Capítulo {numero_capitulo} -> estado final: {datos_decision['estado']}")

    # 6. Inspección final del estado relacional en PostgreSQL
    resultado_estado_final = await app.call_tool("obtener_estado", {"id_proyecto": id_proyecto})
    estado_final = _desenvolver(resultado_estado_final)
    metricas_bd = await _inspeccionar_bd_relacional(id_proyecto)

    print("\n" + "=" * 80)
    print("📊 6. RESUMEN DE ENTIDADES CANÓNICAS MATERIALIZADAS EN POSTGRESQL")
    print("=" * 80)
    print(f"   • Título Oficial (P04)         : {estado_final['titulo']}")
    print(f"   • Código ODS (P03)             : {metricas_bd['codigo_ods']}")
    print(f"   • Versión de Estado            : {metricas_bd['version_bloqueo']}")
    print(f"   • Pasos Completados            : {metricas_bd['pasos_completados']} / 12")
    print(f"   • Capítulos Aprobados          : {metricas_bd['capitulos_aprobados']} / 3")
    print(f"   • Revisiones Inmutables        : {metricas_bd['revisiones_capitulo']}")
    print(f"   • Filas Matriz de Consistencia : {metricas_bd['filas_consistencia']} (1 General + 3 Específicas)")
    print(f"   • Variables Relacionales (P11) : {metricas_bd['variables_investigacion']} (VI + VD)")
    print(f"   • Cruces Fila x Variable       : {metricas_bd['cruces_fila_variable']}")
    print(f"   • Dimensiones Operacionales    : {metricas_bd['dimensiones_variable']}")
    print(f"   • Indicadores Medibles (P12)   : {metricas_bd['indicadores']}")
    print(f"   • Observaciones Resueltas      : {metricas_bd['comentarios_resueltos']}")
    print(f"   • Eventos de Auditoría Docente : {metricas_bd['eventos_revision']}")
    print("=" * 80)
    print("✅ SIMULACIÓN DE AVANCE (CAPÍTULOS 1 AL 3) COMPLETADA AL 100% SIN ERRORES.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(probar_servidor_mcp())
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
