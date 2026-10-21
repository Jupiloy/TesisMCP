"""Registro y publicación de prompts MCP (@app.prompt) en TesisMCP (Capítulos 1 al 3: P01 a P12 + 3 roles)."""

import json
from typing import Any

from mcp.server.mcpserver import MCPServer

from mcp_server.puente_django import configurar_django
configurar_django()

from mcp_server.prompts.hidratacion import hidratar_contexto_proyecto
from mcp_server.prompts.roles import DIRECTIVA_TRIPLE_FASE, ROLES_DIRECTIVAS
from mcp_server.prompts.plantillas import PLANTILLAS_POR_PASO
from thesis.catalogo_pasos import CATALOGO_PASOS


def _crear_manejador_paso(codigo_paso: str, datos_paso: dict[str, Any], plantilla: dict[str, Any]):
    nombre_prompt = plantilla["nombre_prompt"]
    titulo = plantilla["titulo"]
    guia = plantilla["guia_metodologica"].strip()
    esquema_json = json.dumps(plantilla["esquema_json_ejemplo"], indent=2, ensure_ascii=False)
    capitulo = datos_paso["capitulo"]
    objetivo = datos_paso["objetivo"]

    def manejador(id_proyecto: str | None = None, detalle_estudiante: str = "") -> str:
        contexto_bd = hidratar_contexto_proyecto(id_proyecto)
        texto_id_proyecto = id_proyecto if id_proyecto else "UUID_DEL_PROYECTO"

        mensaje = [
            "# 🎓 TesisMCP — Asistente Metodológico de Tesis",
            f"## {titulo} (Capítulo {capitulo})",
            f"**Objetivo:** {objetivo}\n",
            "---",
            contexto_bd,
            "---",
            "## 📚 Guía Metodológica del Paso (Lineamientos UTP y Asesoría)",
            guia,
            "",
            DIRECTIVA_TRIPLE_FASE,
            "",
            "---",
            f"## 📦 Contrato Pydantic y Esquema JSON Requerido para `guardar_paso` ({codigo_paso})",
            "El siguiente JSON es un ejemplo que pasa el contrato Pydantic; sustituye los datos ilustrativos por valores comprobados y respeta los límites del contrato (sin atributos extra):",
            "```json",
            esquema_json,
            "```",
            "",
            "### 💾 Protocolo de Persistencia en PostgreSQL:",
            "Cuando el tesista dé su visto bueno a la redacción:",
            "1. Redacta el contenido en Markdown (`contenido_md`).",
            "2. Construye el objeto JSON estructurado (`datos_salida`).",
            "3. Invoca la herramienta MCP `guardar_paso` con los siguientes parámetros:",
            f"   - `id_proyecto`: \"{texto_id_proyecto}\"",
            f"   - `codigo_paso`: \"{codigo_paso}\"",
            "   - `contenido_md`: (texto en prosa continua)",
            "   - `datos_salida`: (objeto JSON validado)",
            "   - `version_esperada`: (usa la `version_estado` actual reportada arriba)",
            "   - `clave_idempotencia`: (un UUIDv4 nuevo generado para esta llamada)",
        ]

        if detalle_estudiante.strip():
            mensaje.extend([
                "",
                "---",
                "### 📝 Notas / Requerimiento Específico del Tesista:",
                detalle_estudiante.strip(),
            ])

        return "\n".join(mensaje)

    manejador.__name__ = nombre_prompt
    manejador.__doc__ = plantilla["descripcion"]
    return manejador


def registrar_prompts_proyecto(app: MCPServer) -> None:
    """Registra en el servidor MCP los 12 prompts de paso (P01-P12) y los 3 prompts de rol dedicado."""

    for codigo_paso, plantilla in PLANTILLAS_POR_PASO.items():
        datos_paso = CATALOGO_PASOS.get(codigo_paso, {"capitulo": 1, "objetivo": plantilla["titulo"]})
        manejador = _crear_manejador_paso(codigo_paso, datos_paso, plantilla)
        app.prompt(
            name=plantilla["nombre_prompt"],
            title=plantilla["titulo"],
            description=plantilla["descripcion"],
        )(manejador)

    @app.prompt(
        name="rol_asesor_metodologico",
        title="Rol: Asesor Metodológico Principal",
        description="Activa al agente en modo asesor metodológico experto para guiar la formulación teórica y científica.",
    )
    def rol_asesor_metodologico(id_proyecto: str | None = None, consulta: str = "") -> str:
        contexto_bd = hidratar_contexto_proyecto(id_proyecto)
        mensaje = [
            "# 👨‍🏫 TesisMCP — Modo Asesor Metodológico Principal",
            ROLES_DIRECTIVAS["asesor_metodologico"],
            "---",
            contexto_bd,
            "---",
            "### 💬 Instrucción de Sesión:",
            "Actúa como el Asesor Metodológico en diálogo continuo con el tesista. "
            "Revisa la coherencia lógica de su problema, objetivos, variables y operacionalización. "
            "Si el estudiante tiene dudas, guíalo socráticamente aplicando la Taxonomía de Bloom y los lineamientos UTP.",
        ]
        if consulta.strip():
            mensaje.extend(["\n**Consulta inicial del tesista:**", consulta.strip()])
        return "\n".join(mensaje)

    @app.prompt(
        name="rol_investigador_grounded",
        title="Rol: Investigador Grounded (Anti-Alucinaciones)",
        description="Activa al agente en modo auditor de literatura científica y exploración bibliográfica inicial.",
    )
    def rol_investigador_grounded(id_proyecto: str | None = None, tema_o_criterio: str = "") -> str:
        contexto_bd = hidratar_contexto_proyecto(id_proyecto)
        texto_id_proyecto = id_proyecto if id_proyecto else "UUID_DEL_PROYECTO"
        mensaje = [
            "# 🔍 TesisMCP — Modo Investigador Grounded (Auditor Anti-Alucinaciones)",
            ROLES_DIRECTIVAS["investigador_grounded"],
            "---",
            contexto_bd,
            "---",
            "### 🛠️ Herramientas MCP Obligatorias para este Rol:",
            f"* `explorar_idea(id_proyecto='{texto_id_proyecto}')`: Explora literatura inicial en OpenAlex sobre la idea provisional.",
            f"* `buscar_antecedentes_peru(id_proyecto='{texto_id_proyecto}', consulta=...)`: Explora antecedentes nacionales y locales en ALICIA.",
            f"* `buscar_semantic_scholar(id_proyecto='{texto_id_proyecto}', consulta=...)`: Busca literatura internacional con DOI.",
            "",
            "**Regla Fundamental:** No admitas citas sintéticas ni autores no verificados. "
            "Declara honestamente cuando un hallazgo proviene solo de metadatos (`SOLO_METADATOS`).",
        ]
        if tema_o_criterio.strip():
            mensaje.extend(["\n**Tema o criterio a investigar:**", tema_o_criterio.strip()])
        return "\n".join(mensaje)

    @app.prompt(
        name="rol_revisor_contratos",
        title="Rol: Revisor de Contratos y Esquemas Pydantic",
        description="Activa al agente en modo auditor de integridad de datos para validar el JSON antes de llamar a guardar_paso.",
    )
    def rol_revisor_contratos(id_proyecto: str | None = None, paso_a_auditar: str = "P01") -> str:
        contexto_bd = hidratar_contexto_proyecto(id_proyecto)
        codigo_limpio = paso_a_auditar.strip().upper()
        plantilla = PLANTILLAS_POR_PASO.get(codigo_limpio, PLANTILLAS_POR_PASO["P01"])
        esquema_json = json.dumps(plantilla["esquema_json_ejemplo"], indent=2, ensure_ascii=False)

        mensaje = [
            f"# 🛡️ TesisMCP — Modo Revisor de Contratos (Paso {codigo_limpio})",
            ROLES_DIRECTIVAS["revisor_contratos"],
            "---",
            contexto_bd,
            "---",
            f"### Esquema Pydantic Requerido para el Paso {codigo_limpio}:",
            "```json",
            esquema_json,
            "```",
            "",
            "### 🔎 Checklist de Auditoría Pre-Persistencia:",
            "1. ¿Todos los campos requeridos están presentes y tienen el tipo de dato correcto?",
            "2. ¿Se eliminó cualquier campo extra que no figure en el contrato Pydantic?",
            "3. ¿Los textos cumplen con los rangos mínimos y máximos de caracteres/palabras?",
            "4. ¿La `version_esperada` coincide con la `version_estado` actual?",
            "Si todo está conforme, formula el comando final para invocar `guardar_paso`.",
        ]
        return "\n".join(mensaje)
