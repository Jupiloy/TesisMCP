"""Servicio de hidratación contextual desde PostgreSQL para los prompts MCP (Capítulos 1 al 3)."""

from uuid import UUID

from mcp_server.django_bridge import usuario_actual, configurar_django


def hidratar_contexto_proyecto(project_id: str | None = None) -> str:
    """
    Lee de PostgreSQL el estado actual del proyecto y lo formatea como Markdown
    para enriquecer el contexto del prompt antes de entregarlo al LLM.
    """
    if not project_id:
        return (
            "## 📋 Estado del Proyecto en Base de Datos\n"
            "*(No se especificó `project_id`. El asistente trabajará en modo preliminar. "
            "Para vincular el avance con PostgreSQL, proporciona el ID del proyecto).*\n"
        )

    try:
        pid = UUID(str(project_id).strip())
    except (ValueError, TypeError):
        return (
            "## 📋 Estado del Proyecto en Base de Datos\n"
            f"⚠️ El `project_id` proporcionado ('{project_id}') no tiene un formato UUID válido.\n"
        )

    configurar_django()
    from thesis.models import ProgresoPaso
    from thesis.services.projects import obtener_estado_proyecto

    actor = usuario_actual()
    state = obtener_estado_proyecto(actor, pid)

    completed_steps = list(
        ProgresoPaso.objects.filter(project_id=pid, status=ProgresoPaso.Status.COMPLETED)
        .order_by("step_code")
        .values_list("step_code", flat=True)
    )

    pasos_str = ", ".join(completed_steps) if completed_steps else "Ningún paso guardado aún"

    lines = [
        "## 📋 Estado Consolidado del Proyecto en PostgreSQL (Fuente Canónica)",
        f"* **ID del Proyecto:** `{state['project_id']}`",
        f"* **Nombre Clave:** {state['name']}",
        f"* **Título Oficial Registrado:** {state['title'] or 'Pendiente de formulación (P04)'}",
        f"* **Versión Actual de Estado (`lock_version`):** `{state['state_version']}` *(usar como `expected_version` al guardar)*",
        f"* **Pasos Completados:** {pasos_str}",
    ]

    if state.get("ods_code"):
        lines.append(f"* **Alineación ODS:** `{state['ods_code']}`")
    if state.get("idea_provisional"):
        lines.append(f"* **Tema / Idea de Investigación:** {state['idea_provisional']}")
    if state.get("unit_of_analysis") or state.get("place") or state.get("period_text"):
        delim = []
        if state.get("unit_of_analysis"):
            delim.append(f"Unidad: {state['unit_of_analysis']}")
        if state.get("place"):
            delim.append(f"Lugar: {state['place']}")
        if state.get("period_text"):
            delim.append(f"Periodo: {state['period_text']}")
        lines.append(f"* **Delimitación:** {', '.join(delim)}")

    if state.get("problem_statement"):
        lines.append(f"* **Problema Central:** {state['problem_statement']}")

    if state.get("approach"):
        lines.append(f"* **Enfoque Metodológico:** {state['approach']}")

    matrix = state.get("consistency_matrix", [])
    if matrix:
        lines.append("\n### 📐 Matriz de Consistencia Actual:")
        for row in matrix:
            ord_label = "General" if row["ordinal"] == 0 else f"Específico {row['ordinal']}"
            lines.append(f"  * **[{ord_label}]**")
            if row.get("question_text"):
                lines.append(f"    - Pregunta: {row['question_text']}")
            if row.get("objective_text"):
                lines.append(f"    - Objetivo: {row['objective_text']}")
            if row.get("hypothesis_text"):
                lines.append(f"    - Hipótesis: {row['hypothesis_text']}")

    variables = state.get("variables", [])
    if variables:
        lines.append("\n### 🧬 Variables y Operacionalización:")
        for v in variables:
            lines.append(f"  * **Variable ({v['role']}):** {v['name']}")
            for d in v.get("dimensions", []):
                lines.append(f"    - Dimensión: {d['name']}")
                for i in d.get("indicators", []):
                    lines.append(f"      • Indicador: {i['name']} (Escala: {i.get('measurement_scale', 'N/A')})")

    return "\n".join(lines) + "\n"
