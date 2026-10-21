# Explicación de Código: `backend/thesis/services/descubrimiento.py`

## 1. Propósito y ¿Qué hace?
Provee la lógica de servicio para la búsqueda y extracción de metadatos bibliográficos desde Semantic Scholar. Permite a los tesistas consultar artículos por palabra clave y filtrar por rango de años.

## 2. Justificación Técnica y ¿Por qué lo hace?
Aísla la interacción con el cliente HTTP externo de Semantic Scholar de las herramientas MCP y de la API web, formateando las respuestas y adjuntando advertencias anti-alucinación.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Recibe la consulta del usuario y el rango de años.
2. Invoca de manera asíncrona `buscar_articulos_semantic_scholar` en el adaptador HTTP.
3. Formatea la lista de artículos identificando citas influyentes y enlaces DOI.
4. Retorna el resultado advirtiendo que los resúmenes son preliminares y deben ser comprobados a texto completo por el estudiante.

## 4. Componentes y Funciones Clave
* `buscar_semantic_scholar_servicio(query, year_range)`: Servicio de búsqueda académica.

## 5. Relaciones con Otras Capas y Tablas
* **Integración:** Consume [`backend/thesis/integrations/semantic_scholar.py`](../../backend/thesis/integrations/semantic_scholar.py).
* **MCP Tool:** Expuesto por `buscar_semantic_scholar` en [`mcp_server/herramientas_proyecto.py`](../../mcp_server/herramientas_proyecto.py).
