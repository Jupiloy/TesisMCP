# Explicación de Código: `backend/thesis/tests/extended_steps/test_chapter3.py`

## 1. Propósito y ¿Qué hace?
Evalúa en profundidad la **materialización relacional del Capítulo 3 (`P09` a `P12`)**: construcción de filas en la Matriz de Consistencia (`GENERAL` y `SPECIFIC`), creación de las variables independiente (`VI`) y dependiente (`VD`), cruces relacionales en `VariableFilaConsistencia`, descomposición en dimensiones y definición de indicadores medibles con escala en `tesis_indicador`.

## 2. Justificación Técnica y ¿Por qué lo hace?
El Capítulo 3 representa el núcleo metodológico más complejo de una tesis. Esta prueba valida que la información no solo se valide en JSON, sino que exista como grafos relacionales en tablas SQL, garantizando que cada indicador apunte a su dimensión y cada dimensión a su variable.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Prepara un proyecto con los pasos `P01` a `P08` completados.
2. Ejecuta `P09` (objetivos) y comprueba que `FilaConsistencia` tenga 1 fila general y 3 específicas con sus respectivos verbos Bloom.
3. Ejecuta `P10` (hipótesis) y comprueba la sincronización con las preguntas y objetivos.
4. Ejecuta `P11` (variables) y verifica la creación de 2 variables y 8 enlaces en `VariableFilaConsistencia`.
5. Ejecuta `P12` (operacionalización) y verifica la persistencia de dimensiones e indicadores con escala `ORDINAL` o `RAZON`.

## 4. Componentes y Funciones Clave
* `test_materializacion_completa_capitulo_3`: Verificación relacional profunda.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Auditadas:** `tesis_fila_consistencia`, `tesis_variable_investigacion`, `tesis_variable_fila_consistencia`, `tesis_dimension_variable`, `tesis_indicador`.
* **Materializador:** [`consistency.py`](../../backend/thesis/services/step_materializers/consistency.md).
