# Explicación de Código: `backend/thesis/services/step_materializers/consistency.py`

## 1. Propósito y ¿Qué hace?
Es el **materializador relacional central** de la versión reducida V1. Toma el diccionario JSON validado de cada paso (`P01` a `P12`) y descompone su información en filas y relaciones dentro de las tablas de PostgreSQL:
* En `P03`: Actualiza el código y argumento ODS en `PerfilInvestigacion`.
* En `P04`: Actualiza el título oficial, unidad de análisis, lugar y periodo.
* En `P06`: Materializa la pregunta general y específicas en `FilaConsistencia`.
* En `P09`: Materializa los objetivos general y específicos en `FilaConsistencia`.
* En `P10`: Materializa las hipótesis general, nula y específicas en `FilaConsistencia`.
* En `P11`: Crea las entidades `VariableInvestigacion` (`VI` y `VD`) y las vincula con las filas de consistencia mediante `VariableFilaConsistencia`.
* En `P12`: Descompone cada variable en `DimensionVariable` y sus respectivos registros de `Indicador` con su escala de medición.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Evita el Síndrome de "Caja Negra":** Los sistemas ingenuos basados en LLMs almacenan las respuestas como simples cadenas de texto. TesisMCP descompone el razonamiento metodológico en una base de datos relacional (3NF), lo que permite que consultas SQL verifiquen si la cantidad de objetivos coincide con la cantidad de preguntas y si cada variable cuenta con indicadores medibles.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Se invoca dentro del bloque `transaction.atomic()` de `guardar_paso_servicio`.
2. Para `P06`:
   - Crea/actualiza `FilaConsistencia(project=project, orden=0, question=pregunta_general)`.
   - Crea las filas específicas con `orden = 1..N`.
3. Para `P09` y `P10`:
   - Busca las filas de consistencia existentes y actualiza los campos `objective` e `hypothesis`.
4. Para `P11`:
   - Crea `VariableInvestigacion` tipo `INDEPENDENT` y `DEPENDENT`.
   - Para cada fila de consistencia, crea registros de enlace en `VariableFilaConsistencia`.
5. Para `P12`:
   - Itera sobre las variables, crea sus registros en `DimensionVariable` y asocia los `Indicador` correspondientes.

## 4. Componentes y Funciones Clave
* `materializar_paso_capitulos_1_a_3(...)`: Función principal que ejecuta la descomposición relacional según el código de paso.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Afectadas:** `tesis_perfil_investigacion`, `tesis_fila_consistencia`, `tesis_variable_investigacion`, `tesis_variable_fila_consistencia`, `tesis_dimension_variable`, `tesis_indicador`.
* **Pruebas:** Evaluado a fondo en [`backend/thesis/tests/extended_steps/test_chapter3.py`](../../backend/thesis/tests/extended_steps/test_chapter3.py).
