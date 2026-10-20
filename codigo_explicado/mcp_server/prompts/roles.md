# Explicación de Código: `mcp_server/prompts/roles.py`

## 1. Propósito y ¿Qué hace?
Define los textos e instrucciones de sistema para los **3 prompts de roles especializados** disponibles en el servidor MCP:
1. `rol_asesor_metodologico`: Instruye al LLM para actuar como un asesor de tesis universitario estricto, guiando la formulación teórica y científica según las normas de la UTP.
2. `rol_investigador_grounded`: Configura al LLM bajo la regla de oro de **cero alucinaciones bibliográficas**, exigiendo que cualquier cita provenga de metadatos o documentos comprobables.
3. `rol_revisor_contratos`: Activa al LLM en modo auditor técnico para que revise y limpie el JSON generado antes de enviarlo a `guardar_paso`, asegurando que cumpla con los esquemas Pydantic V2.

## 2. Justificación Técnica y ¿Por qué lo hace?
Un único prompt genérico no puede asesorar metodológicamente, buscar fuentes y validar contratos JSON simultáneamente con la máxima precisión. Dividir la asistencia en roles especializados reduce errores y optimiza el razonamiento del modelo de lenguaje para cada tarea.

## 3. Mecanismo Interno y ¿Cómo lo hace?
Provee cadenas de texto formateadas con directrices operativas, límites deontológicos y reglas de formato que se ensamblan en objetos `PromptMessage(role="user", content=TextContent(...))`.

## 4. Componentes y Funciones Clave
* `TEXTO_ASESOR_METODOLOGICO`: Instrucciones de asesoría científica.
* `TEXTO_INVESTIGADOR_GROUNDED`: Instrucciones de búsqueda e imparcialidad científica.
* `TEXTO_REVISOR_CONTRATOS`: Instrucciones de validación de contratos JSON.

## 5. Relaciones con Otras Capas y Tablas
* **Catálogo:** Registrado en [`mcp_server/prompts/catalog.py`](./catalog.md).
