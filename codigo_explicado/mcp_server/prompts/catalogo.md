# Explicación de Código: `mcp_server/prompts/catalogo.py`

## 1. Propósito y ¿Qué hace?
Registra los **15 prompts MCP dinámicos** en la instancia de `MCPServer`:
* **12 Prompts Metodológicos (`paso_p01_mapa_temas` a `paso_p12_operacionalizacion`):** Guían la redacción de cada paso inyectando el contexto acumulado de la tesis.
* **3 Prompts de Roles Especializados (`rol_asesor_metodologico`, `rol_investigador_grounded`, `rol_revisor_contratos`):** Configuran el comportamiento y las directrices del LLM.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Context Injection:** Los LLMs no recuerdan el título o los objetivos definidos en pasos previos a menos que se les inyecten en el prompt. Este catálogo define prompts parametrizados por `id_proyecto` que consultan PostgreSQL en vivo antes de devolver la plantilla al agente.
* **Consistencia Metodológica:** Garantiza que la estructura exigida en los prompts coincida exactamente con las restricciones de los contratos Pydantic en `contratos_pasos.py`.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Declara la función `registrar_prompts(app: MCPServer)`.
2. Para cada paso metodológico decora una función con `@app.prompt(name=...)` recibiendo el argumento `id_proyecto`.
3. La función invoca `hidratar_contexto_proyecto(id_proyecto)` de `hydration.py` para obtener el estado real de la tesis.
4. Concatena la plantilla del paso (obtenida de `templates/`) con el contexto hidratado y retorna los mensajes en formato estándar `PromptMessage`.
5. Registra los 3 roles especializados sin requerir argumentos de proyecto.

## 4. Componentes y Funciones Clave
* `registrar_prompts(app)`: Registrador oficial de los 15 prompts.
* 12 prompts de pasos con hidratación dinámica.
* 3 prompts de rol de agente.

## 5. Relaciones con Otras Capas y Tablas
* **Motor de Hidratación:** Consume [`hydration.py`](./hydration.md).
* **Plantillas:** Consume [`templates/`](./templates.md) y [`roles.py`](./roles.md).
* **Auditoría:** Verificado por [`backend/thesis/tests/test_prompts_mcp.py`](../../tests/test_prompts_mcp.md).
