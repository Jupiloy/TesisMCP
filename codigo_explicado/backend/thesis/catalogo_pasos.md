# Explicación de Código: `backend/thesis/catalogo_pasos.py`

## 1. Propósito y ¿Qué hace?
Define el **catálogo declarativo canónico** de los 12 pasos metodológicos implementados (`P01` a `P12`), pertenecientes exclusivamente a los Capítulos 1, 2 y 3. Es la fuente única de verdad (*Single Source of Truth*) para conocer qué capítulo contiene a cada paso, cuál es su título formal, qué campos de entrada exige y qué objetivo metodológico persigue.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Evita Hardcoding:** En lugar de dispersar códigos `P01`, `P02`, etc., en múltiples condicionales a lo largo de vistas y herramientas MCP, el catálogo centraliza las definiciones en una estructura inmutable.
* **Filtro del alcance del avance V1:** Si se solicita un paso fuera de alcance (`P13` en adelante), este catálogo no lo contiene, permitiendo que la capa de servicios rechace peticiones inválidas con `ERROR_VALIDACION` antes de tocar la base de datos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Define el diccionario `CATALOGO_PASOS: dict[str, dict]`.
2. Para cada paso (`P01` a `P12`), especifica:
   - `codigo`: Identificador alfanumérico estandarizado (`P01`...`P12`).
   - `capitulo`: Número de capítulo (1, 2 o 3).
   - `titulo`: Nombre formal del paso metodológico.
   - `descripcion`: Objetivo académico y pedagógico del paso.
   - `campos_requeridos`: Lista de atributos que el JSON debe contener obligatoriamente.
3. Provee funciones utilitarias `obtener_paso(codigo)` y `listar_pasos_por_capitulo(capitulo)`.

## 4. Componentes y Funciones Clave
* `CATALOGO_PASOS`: Diccionario canónico de 12 pasos activos.
* `PASOS_CAPITULO_1`: `['P01', 'P02', 'P03', 'P04', 'P05']` (Elección del tema y alcance).
* `PASOS_CAPITULO_2`: `['P06', 'P07', 'P08']` (Realidad problemática y justificación).
* `PASOS_CAPITULO_3`: `['P09', 'P10', 'P11', 'P12']` (Objetivos, hipótesis y operacionalización).

## 5. Relaciones con Otras Capas y Tablas
* **Contratos:** Cada código en `CATALOGO_PASOS` se mapea a un esquema en [`backend/thesis/services/contratos_pasos.py`](../../backend/thesis/services/contratos_pasos.py).
* **Servidor MCP:** Es consultado por las herramientas `listar_pasos_mvp` y `consultar_detalle_paso` en [`mcp_server/server.py`](../../mcp_server/server.py).
* **Verificación:** Auditado matemáticamente por [`scripts/verify_project.py`](../../scripts/verify_project.py) (exige exactamente 12 pasos en capítulos 1 al 3).
