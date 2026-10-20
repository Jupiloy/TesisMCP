# Explicación de Código: `backend/thesis/integrations/openalex.py`

## 1. Propósito y ¿Qué hace?
Es el adaptador HTTP para la API abierta de **OpenAlex**, catálogo global de literatura científica indexada con más de 250 millones de obras académicas.

## 2. Justificación Técnica y ¿Por qué lo hace?
A diferencia de servicios comerciales con claves cerradas y costos por consulta, OpenAlex ofrece un índice bibliográfico abierto, altamente disponible y con soporte para búsqueda semántica por conceptos, identificadores DOI y filiaciones institucionales.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Configura `httpx.AsyncClient(base_url="https://api.openalex.org")`.
2. Consulta el endpoint `/works` aplicando filtros de relevancia y rango de años (`from_publication_date`).
3. Extrae metadatos normalizados: título del artículo, revista/conferencia, autores, resumen (reconstruyendo el índice invertido de OpenAlex), citas y DOI.
4. Advierte formalmente que los resultados son metadatos y no implican disponibilidad de texto completo.

## 4. Componentes y Funciones Clave
* `buscar_obras_openalex(query: str, limit: int = 10) -> list[dict]`: Búsqueda de literatura global.
* `reconstruir_resumen_invertido(abstract_inverted_index: dict) -> str`: Algoritmo que reconstruye el texto del resumen a partir del mapa de posiciones de OpenAlex.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** Consumido por [`backend/thesis/services/exploration.py`](../../backend/thesis/services/exploration.py).
* **Herramienta MCP:** Invocado por `explorar_idea` en [`mcp_server/project_tools.py`](../../mcp_server/project_tools.py).
