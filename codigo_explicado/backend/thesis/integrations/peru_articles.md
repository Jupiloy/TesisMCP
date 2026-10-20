# Explicación de Código: `backend/thesis/integrations/peru_articles.py`

## 1. Propósito y ¿Qué hace?
Es un adaptador especializado que consulta la API de OpenAlex aplicando filtros estrictos de filiación institucional por país (`institutions.country_code: PE`), localizando artículos publicados en revistas indexadas cuyos autores pertenecen a universidades o centros de investigación peruanos.

## 2. Justificación Técnica y ¿Por qué lo hace?
Distingue entre tesis de pregrado peruanas (obtenidas desde ALICIA) y artículos científicos de investigación con revisión por pares publicados por investigadores en el Perú, enriqueciendo el banco de antecedentes nacionales del estudiante.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Configura una consulta a OpenAlex añadiendo el parámetro `filter=institutions.country_code:PE`.
2. Itera sobre la lista de instituciones y autores del artículo para comprobar que al menos una filiación pertenezca a una universidad o entidad peruana.
3. Extrae metadatos y enlaces de acceso abierto (Open Access).

## 4. Componentes y Funciones Clave
* `buscar_articulos_peru(query: str, limit: int = 10) -> list[dict]`: Búsqueda de publicaciones con filiación peruana.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** Invocado por [`backend/thesis/services/discovery_peru.py`](../../backend/thesis/services/discovery_peru.py).
* **Herramienta MCP:** Apoya a la herramienta `buscar_antecedentes_peru`.
