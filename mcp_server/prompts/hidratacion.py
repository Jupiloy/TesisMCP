"""Servicio de hidratación contextual desde PostgreSQL para los prompts MCP (Capítulos 1 al 3)."""

from uuid import UUID

from mcp_server.puente_django import usuario_actual, configurar_django


def hidratar_contexto_proyecto(id_proyecto: str | None = None) -> str:
    """
    Lee de PostgreSQL el estado actual del proyecto y lo formatea como Markdown
    para enriquecer el contexto del prompt antes de entregarlo al LLM.
    """
    if not id_proyecto:
        return (
            "## 📋 Estado del Proyecto en Base de Datos\n"
            "*(No se especificó `id_proyecto`. El asistente trabajará en modo preliminar. "
            "Para vincular el avance con PostgreSQL, proporciona el ID del proyecto).*\n"
        )

    try:
        id_uuid = UUID(str(id_proyecto).strip())
    except (ValueError, TypeError):
        return (
            "## 📋 Estado del Proyecto en Base de Datos\n"
            f"⚠️ El `id_proyecto` proporcionado ('{id_proyecto}') no tiene un formato UUID válido.\n"
        )

    configurar_django()
    from thesis.models import ProgresoPaso
    from thesis.services.proyectos import obtener_estado_proyecto

    usuario = usuario_actual()
    estado = obtener_estado_proyecto(usuario, id_uuid)

    pasos_completados = list(
        ProgresoPaso.objects.filter(project_id=id_uuid, status=ProgresoPaso.Status.COMPLETADO)
        .order_by("step_code")
        .values_list("step_code", flat=True)
    )

    texto_pasos = ", ".join(pasos_completados) if pasos_completados else "Ningún paso guardado aún"

    lineas = [
        "## 📋 Estado Consolidado del Proyecto en PostgreSQL (Fuente Canónica)",
        f"* **ID del Proyecto:** `{estado['id_proyecto']}`",
        f"* **Nombre Clave:** {estado['nombre']}",
        f"* **Título Oficial Registrado:** {estado['titulo'] or 'Pendiente de formulación (P04)'}",
        f"* **Versión Actual de Estado (`version_estado`):** `{estado['version_estado']}` *(usar como `version_esperada` al guardar)*",
        f"* **Pasos Completados:** {texto_pasos}",
    ]

    if estado.get("codigo_ods"):
        lineas.append(f"* **Alineación ODS:** `{estado['codigo_ods']}`")
    if estado.get("idea_provisional"):
        lineas.append(f"* **Tema / Idea de Investigación:** {estado['idea_provisional']}")
    if estado.get("unidad_analisis") or estado.get("lugar") or estado.get("periodo_texto"):
        delimitacion = []
        if estado.get("unidad_analisis"):
            delimitacion.append(f"Unidad: {estado['unidad_analisis']}")
        if estado.get("lugar"):
            delimitacion.append(f"Lugar: {estado['lugar']}")
        if estado.get("periodo_texto"):
            delimitacion.append(f"Periodo: {estado['periodo_texto']}")
        lineas.append(f"* **Delimitación:** {', '.join(delimitacion)}")

    if estado.get("planteamiento_problema"):
        lineas.append(f"* **Problema Central:** {estado['planteamiento_problema']}")

    if estado.get("enfoque"):
        lineas.append(f"* **Enfoque Metodológico:** {estado['enfoque']}")

    matriz = estado.get("matriz_consistencia", [])
    if matriz:
        lineas.append("\n### 📐 Matriz de Consistencia Actual:")
        for fila in matriz:
            etiqueta_orden = "General" if fila["orden"] == 0 else f"Específico {fila['orden']}"
            lineas.append(f"  * **[{etiqueta_orden}]**")
            if fila.get("texto_pregunta"):
                lineas.append(f"    - Pregunta: {fila['texto_pregunta']}")
            if fila.get("texto_objetivo"):
                lineas.append(f"    - Objetivo: {fila['texto_objetivo']}")
            if fila.get("texto_hipotesis"):
                lineas.append(f"    - Hipótesis: {fila['texto_hipotesis']}")

    variables = estado.get("variables", [])
    if variables:
        lineas.append("\n### 🧬 Variables y Operacionalización:")
        for variable in variables:
            lineas.append(f"  * **Variable ({variable['rol']}):** {variable['nombre']}")
            for dimension in variable.get("dimensiones", []):
                lineas.append(f"    - Dimensión: {dimension['nombre']}")
                for indicador in dimension.get("indicadores", []):
                    lineas.append(
                        f"      • Indicador: {indicador['nombre']} "
                        f"(Escala: {indicador.get('escala_medicion', 'N/A')})"
                    )

    return "\n".join(lineas) + "\n"
