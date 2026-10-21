# Explicación de Código: `backend/thesis/integrations/alicia.py`

## 1. Propósito y ¿Qué hace?
Es el adaptador HTTP que conecta con el repositorio nacional **ALICIA (Acceso Libre a Información Científica para la Innovación)** del CONCYTEC en Perú. Permite buscar tesis de grado y posgrado sustentadas en universidades peruanas.

## 2. Justificación Técnica y ¿Por qué lo hace?
ALICIA es el repositorio oficial estatal que indexa la producción académica nacional. La integración con este repositorio garantiza que las búsquedas de antecedentes nacionales en TesisMCP provengan de repositorios oficiales acreditados por el Estado peruano.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Emplea `httpx.AsyncClient` con tiempo de espera configurado (`timeout=10.0`).
2. Realiza peticiones GET a la API pública OAI-PMH / OpenSearch de ALICIA.
3. Parsea los metadatos XML / JSON extrayendo: título, autor(es), asesor, universidad otorgante del grado, año y enlace al repositorio institucional.
4. Si el servicio de ALICIA experimenta latencia o caída, captura `httpx.HTTPError` y devuelve una respuesta vacía estructurada sin interrumpir el funcionamiento de TesisMCP.

## 4. Componentes y Funciones Clave
* `buscar_tesis_alicia(termino: str, limite: int = 10) -> list[dict]`: Función asíncrona de consulta.
* Manejo seguro de timeouts y errores de conexión con backoff preventivo.

## 5. Relaciones con Otras Capas y Tablas
* **Servicio:** Consumido por [`backend/thesis/services/descubrimiento_peru.py`](../../backend/thesis/services/descubrimiento_peru.py).
* **Herramienta MCP:** Llamado indirectamente desde `buscar_antecedentes_peru`.
