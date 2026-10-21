# Explicación de Código: `backend/thesis/integrations/semantic_scholar.py`

## 1. Propósito y ¿Qué hace?
Es el adaptador HTTP hacia la API de **Semantic Scholar** (del Allen Institute for AI), permitiendo consultar artículos científicos, conteo de citas influyentes y campos temáticos de ingeniería y ciencias de la computación.

## 2. Justificación Técnica y ¿Por qué lo hace?
Semantic Scholar destaca en el área de ingeniería de software e inteligencia artificial por su capacidad de identificar citas influyentes (*influential citations*) y grafos de citación, lo que ayuda al tesista a priorizar los artículos más relevantes de su área.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Utiliza `httpx.AsyncClient` apuntando al endpoint oficial `https://api.semanticscholar.org/graph/v1/paper/search`.
2. Solicita los campos específicos: `title,authors,year,abstract,citationCount,influentialCitationCount,url`.
3. Maneja de forma tolerante a fallos la limitación de tasa (*rate limiting*) mediante cabeceras y control de excepciones.

## 4. Componentes y Funciones Clave
* `buscar_articulos_semantic_scholar(query: str, limit: int = 10, year_range: str = None) -> list[dict]`.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** Consumido por [`backend/thesis/services/descubrimiento.py`](../../backend/thesis/services/descubrimiento.py).
* **Herramienta MCP:** Invocado por `buscar_semantic_scholar` en [`mcp_server/herramientas_proyecto.py`](../../mcp_server/herramientas_proyecto.py).
