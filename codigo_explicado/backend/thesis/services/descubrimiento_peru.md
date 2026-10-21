# Explicación de Código: `backend/thesis/services/descubrimiento_peru.py`

## 1. Propósito y ¿Qué hace?
Orquesta la búsqueda de antecedentes nacionales peruanos para la formulación inicial de la tesis. Consulta simultáneamente el repositorio nacional **ALICIA (CONCYTEC)** para tesis de grado y la API de **OpenAlex** para artículos con filiación en instituciones peruanas (`country_code: PE`), aplicando deduplicación y detección de ámbito geográfico.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Requisito Metodológico UTP:** Toda tesis universitaria en el Perú debe documentar antecedentes nacionales e internacionales. Este servicio provee una herramienta unificada para explorar la literatura peruana sin salir del entorno de desarrollo.
* **Política Anti-Alucinación:** Advierte de manera explícita que las respuestas corresponden a metadatos de búsqueda bibliográfica preliminar y no a comprobación física de PDFs a texto completo.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Recibe la consulta temática del estudiante y el rango de años deseado.
2. Invoca de forma asíncrona:
   - `buscar_tesis_alicia(query)` en el adaptador de ALICIA.
   - `buscar_articulos_peru(query)` en el adaptador de OpenAlex Perú.
3. Normaliza las respuestas en una estructura común con título, autores, año, institución, enlace y fuente.
4. Identifica menciones de departamentos o regiones peruanas mediante `inferir_ambito_geografico`.
5. Retorna la lista consolidada acompañada de la advertencia metodológica formal.

## 4. Componentes y Funciones Clave
* `buscar_antecedentes_peru_servicio(...)`: Orquestador de antecedentes nacionales.
* `ADVERTENCIA_METADATOS_PERU`: Mensaje estricto de rigor científico.

## 5. Relaciones con Otras Capas y Tablas
* **Integraciones:** Consume [`backend/thesis/integrations/alicia.py`](../../backend/thesis/integrations/alicia.py) y [`articulos_peru.py`](../../backend/thesis/integrations/articulos_peru.py).
* **Servicio Auxiliar:** Utiliza [`backend/thesis/services/geografia.py`](../../backend/thesis/services/geografia.py).
* **Herramienta MCP:** Expuesto por `buscar_antecedentes_peru` en [`mcp_server/herramientas_proyecto.py`](../../mcp_server/herramientas_proyecto.py).
