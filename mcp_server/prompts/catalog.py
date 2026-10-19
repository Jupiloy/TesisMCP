"""Registro y publicación de prompts MCP (@app.prompt) en TesisMCP (Capítulos 1 al 3: P01 a P12 + 3 roles)."""

import json
from typing import Any

from mcp.server.mcpserver import MCPServer

from mcp_server.django_bridge import configurar_django
configurar_django()

from mcp_server.prompts.hydration import hidratar_contexto_proyecto
from mcp_server.prompts.roles import DIRECTIVA_TRIPLE_FASE, ROLES_DIRECTIVAS
from mcp_server.prompts.templates import TEMPLATES_POR_PASO
from thesis.step_catalogue import CATALOGO_PASOS


def _crear_handler_paso(step_code: str, step_info: dict[str, Any], template: dict[str, Any]):
    prompt_name = template["prompt_name"]
    titulo = template["titulo"]
    guia = template["guia_metodologica"].strip()
    esquema_json = json.dumps(template["esquema_json_ejemplo"], indent=2, ensure_ascii=False)
    capitulo = step_info["capitulo"]
    objetivo = step_info["objetivo"]

    def manejador(project_id: str | None = None, detalle_estudiante: str = "") -> str:
        ctx_bd = hidratar_contexto_proyecto(project_id)
        pid_text = project_id if project_id else "UUID_DEL_PROYECTO"

        mensaje = [
            "# 🎓 TesisMCP — Asistente Metodológico de Tesis",
            f"## {titulo} (Capítulo {capitulo})",
            f"**Objetivo:** {objetivo}\n",
            "---",
            ctx_bd,
            "---",
            "## 📚 Guía Metodológica del Paso (Lineamientos UTP y Asesoría)",
            guia,
            "",
            DIRECTIVA_TRIPLE_FASE,
            "",
            "---",
            f"## 📦 Contrato Pydantic y Esquema JSON Requerido para `guardar_paso` ({step_code})",
            "El siguiente JSON es un ejemplo que pasa el contrato Pydantic; sustituye los datos ilustrativos por valores comprobados y respeta los límites del contrato (sin atributos extra):",
            "```json",
            esquema_json,
            "```",
            "",
            "### 💾 Protocolo de Persistencia en PostgreSQL:",
            "Cuando el tesista dé su visto bueno a la redacción:",
            "1. Redacta el contenido en Markdown (`content_md`).",
            "2. Construye el objeto JSON estructurado (`output_data`).",
            "3. Invoca la herramienta MCP `guardar_paso` con los siguientes parámetros:",
            f"   - `project_id`: \"{pid_text}\"",
            f"   - `step_code`: \"{step_code}\"",
            "   - `content_md`: (texto en prosa continua)",
            "   - `output_data`: (objeto JSON validado)",
            "   - `expected_version`: (usa el `lock_version` actual reportado arriba en el estado de BD)",
            "   - `idempotency_key`: (un UUIDv4 nuevo generado para esta llamada)",
        ]

        if detalle_estudiante.strip():
            mensaje.extend([
                "",
                "---",
                "### 📝 Notas / Requerimiento Específico del Tesista:",
                detalle_estudiante.strip(),
            ])

        return "\n".join(mensaje)

    manejador.__name__ = prompt_name
    manejador.__doc__ = template["descripcion"]
    return manejador


def registrar_prompts_proyecto(app: MCPServer) -> None:
    """Registra en el servidor MCP los 12 prompts de paso (P01-P12) y los 3 prompts de rol dedicado."""

    for step_code, template in TEMPLATES_POR_PASO.items():
        step_info = CATALOGO_PASOS.get(step_code, {"capitulo": 1, "objetivo": template["titulo"]})
        manejador = _crear_handler_paso(step_code, step_info, template)
        app.prompt(
            name=template["prompt_name"],
            title=template["titulo"],
            description=template["descripcion"],
        )(manejador)

    @app.prompt(
        name="rol_asesor_metodologico",
        title="Rol: Asesor Metodológico Principal",
        description="Activa al agente en modo asesor metodológico experto para guiar la formulación teórica y científica.",
    )
    def rol_asesor_metodologico(project_id: str | None = None, consulta: str = "") -> str:
        ctx_bd = hidratar_contexto_proyecto(project_id)
        mensaje = [
            "# 👨‍🏫 TesisMCP — Modo Asesor Metodológico Principal",
            ROLES_DIRECTIVAS["asesor_metodologico"],
            "---",
            ctx_bd,
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
    def rol_investigador_grounded(project_id: str | None = None, tema_o_criterio: str = "") -> str:
        ctx_bd = hidratar_contexto_proyecto(project_id)
        pid_text = project_id if project_id else "UUID_DEL_PROYECTO"
        mensaje = [
            "# 🔍 TesisMCP — Modo Investigador Grounded (Auditor Anti-Alucinaciones)",
            ROLES_DIRECTIVAS["investigador_grounded"],
            "---",
            ctx_bd,
            "---",
            "### 🛠️ Herramientas MCP Obligatorias para este Rol:",
            f"* `explorar_idea(project_id='{pid_text}')`: Explora literatura inicial en OpenAlex sobre la idea provisional.",
            f"* `buscar_antecedentes_peru(project_id='{pid_text}', query=...)`: Explora antecedentes nacionales y locales en ALICIA.",
            f"* `buscar_semantic_scholar(project_id='{pid_text}', query=...)`: Busca literatura internacional con DOI.",
            "",
            "**Regla Fundamental:** No admitas citas sintéticas ni autores no verificados. "
            "Declara honestamente cuando un hallazgo proviene solo de metadatos (`METADATA_ONLY`).",
        ]
        if tema_o_criterio.strip():
            mensaje.extend(["\n**Tema o criterio a investigar:**", tema_o_criterio.strip()])
        return "\n".join(mensaje)

    @app.prompt(
        name="rol_revisor_contratos",
        title="Rol: Revisor de Contratos y Esquemas Pydantic",
        description="Activa al agente en modo auditor de integridad de datos para validar el JSON antes de llamar a guardar_paso.",
    )
    def rol_revisor_contratos(project_id: str | None = None, paso_a_auditar: str = "P01") -> str:
        ctx_bd = hidratar_contexto_proyecto(project_id)
        step_clean = paso_a_auditar.strip().upper()
        template = TEMPLATES_POR_PASO.get(step_clean, TEMPLATES_POR_PASO["P01"])
        esquema_json = json.dumps(template["esquema_json_ejemplo"], indent=2, ensure_ascii=False)

        mensaje = [
            f"# 🛡️ TesisMCP — Modo Revisor de Contratos (Paso {step_clean})",
            ROLES_DIRECTIVAS["revisor_contratos"],
            "---",
            ctx_bd,
            "---",
            f"### Esquema Pydantic Requerido para el Paso {step_clean}:",
            "```json",
            esquema_json,
            "```",
            "",
            "### 🔎 Checklist de Auditoría Pre-Persistencia:",
            "1. ¿Todos los campos requeridos están presentes y tienen el tipo de dato correcto?",
            "2. ¿Se eliminó cualquier campo extra que no figure en el contrato Pydantic?",
            "3. ¿Los textos cumplen con los rangos mínimos y máximos de caracteres/palabras?",
            "4. ¿El `expected_version` coincide con el `lock_version` actual de PostgreSQL?",
            "Si todo está conforme, formula el comando final para invocar `guardar_paso`.",
        ]
        return "\n".join(mensaje)
