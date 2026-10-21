# Explicación de Código: `backend/thesis/tests/test_prompts_mcp.py`

## 1. Propósito y ¿Qué hace?
Verifica el servidor de prompts del protocolo MCP: comprueba que exactamente **15 prompts** estén registrados en `MCPServer`, valida que los 12 prompts de pasos requieran el parámetro `id_proyecto` y comprueba que la **hidratación dinámica** inyecte los datos reales de PostgreSQL dentro del prompt antes de entregarlo al LLM.

## 2. Justificación Técnica y ¿Por qué lo hace?
Garantiza que el agente de IA reciba instrucciones contextualizadas con el título, variables y objetivos confirmados de la tesis, impidiendo que el LLM trabaje "a ciegas" o con datos desactualizados.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Consulta `app.list_prompts()` y valida `len(prompts) == 15`.
2. Verifica que existan los 3 roles (`rol_asesor_metodologico`, `rol_investigador_grounded`, `rol_revisor_contratos`).
3. Invoca `app.get_prompt("paso_p10_preguntas_hipotesis", {"id_proyecto": str(proyecto.id)})` y comprueba que el texto devuelto contenga el título oficial guardado en `P04`.

## 4. Componentes y Funciones Clave
* Pruebas de registro e hidratación en vivo de prompts MCP.

## 5. Relaciones con Otras Capas y Tablas
* **Servidor MCP:** [`mcp_server/prompts/catalogo.py`](../../mcp_server/prompts/catalogo.md) y [`hidratacion.py`](../../mcp_server/prompts/hidratacion.md).
