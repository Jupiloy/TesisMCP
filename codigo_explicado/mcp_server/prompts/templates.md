# Explicación de Código: `mcp_server/prompts/templates/`

## 1. Propósito y ¿Qué hace?
Agrupa los módulos con las **plantillas de prompts metodológicos** organizadas por capítulo:
* `chapter_1.py`: Plantillas para `P01` (mapa de temas), `P02` (tipo de investigación), `P03` (población y ODS), `P04` (título) y `P05` (alcance).
* `chapter_2.py`: Plantillas para `P06` (problema estructurado `CA-S-P-CO-CC-PC`), `P07` (preguntas) y `P08` (justificaciones).
* `chapter_3.py`: Plantillas para `P09` (objetivos Bloom), `P10` (hipótesis), `P11` (variables `VI`/`VD`) y `P12` (operacionalización).

## 2. Justificación Técnica y ¿Por qué lo hace?
Cada paso metodológico tiene criterios científicos específicos (verbos de la taxonomía de Bloom en `P09`, coherencia biunívoca en `P10`, escalas de medición en `P12`). Mantener plantillas modulares facilita su mantenimiento y sincronización con las normas universitarias de la UTP.

## 3. Mecanismo Interno y ¿Cómo lo hace?
Cada módulo expone funciones o constantes con el texto base del prompt, indicando los objetivos del paso, ejemplos de redacción, campos obligatorios de salida y directrices de formato Markdown.

## 4. Componentes y Funciones Clave
* Plantillas `PLANTILLA_P01` a `PLANTILLA_P12` con instrucciones metodológicas precisas.

## 5. Relaciones con Otras Capas y Tablas
* **Contratos:** Las instrucciones de salida coinciden estrictamente con los esquemas de [`backend/thesis/services/step_contracts.py`](../../backend/thesis/services/step_contracts.py).
* **Catálogo:** Ensambladas por [`mcp_server/prompts/catalog.py`](./catalog.md).
