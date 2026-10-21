# Explicación de Código: `backend/thesis/models/research.py`

## 1. Propósito y ¿Qué hace?
Contiene los modelos del **núcleo metodológico y científico** de la tesis para los Capítulos 1 al 3:
* `PerfilInvestigacion` (`tesis_perfil_investigacion`): Parámetros metodológicos globales (enfoque, ODS, unidad de análisis, lugar, periodo, planteamiento) y el contador `lock_version` para control de concurrencia optimista.
* `FilaConsistencia` (`tesis_fila_consistencia`): Filas de la **Matriz de Consistencia** (orden 0 para el problema/objetivo/hipótesis general, y 1..N para los específicos).
* `VariableInvestigacion` (`tesis_variable_investigacion`): Definición formal de la Variable Independiente (`VI`) y Variable Dependiente (`VD`).
* `VariableFilaConsistencia` (`tesis_variable_fila_consistencia`): Tabla puente de cruce entre filas de consistencia y variables.
* `DimensionVariable` (`tesis_dimension_variable`): Descomposición en dimensiones de cada variable.
* `Indicador` (`tesis_indicador`): Indicadores empíricos medibles con escala de medición (`NOMINAL`, `ORDINAL`, `INTERVALO`, `RAZON`).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Normalización vs Blobs JSON:** En lugar de guardar la tesis como un único texto opaco, este módulo normaliza la investigación en 3NF en PostgreSQL. Esto permite validar matemáticamente que cada objetivo específico corresponda a una pregunta específica, a una hipótesis específica y a variables mensurables.
* **Control de Concurrencia Optimista (OCC):** El campo `lock_version` en `PerfilInvestigacion` evita que peticiones concurrentes desde el IDE y la web sobreescriban los datos del compañero (*Lost Update*).

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `PerfilInvestigacion`: Vinculado 1:1 con `Proyecto`. Contiene `lock_version = IntegerField(default=1, db_column="version_bloqueo")`. Cada guardado exitoso incrementa este valor de forma transaccional.
2. `FilaConsistencia`: `orden=0` identifica la fila de nivel general. Filas con `orden > 0` son de nivel específico. Garantiza que la formulación del problema (`P06`/`P07`), objetivos (`P09`) e hipótesis (`P10`) compartan la misma tupla física.
3. `VariableInvestigacion`: Define el tipo `INDEPENDENT`, `DEPENDENT` o `OTHER` con restricción de orden.
4. `DimensionVariable` e `Indicador`: Estructuran la Matriz de Operacionalización de `P12`.

## 4. Componentes y Funciones Clave
* `PerfilInvestigacion`: Estado consolidado y versión del proyecto.
* `FilaConsistencia`: Representación relacional de la Matriz de Consistencia.
* `TipoVariable`: Enumeración de tipos de variable metodológica.
* `EscalaMedicion`: Escalas estadísticas admitidas (`NOMINAL`, `ORDINAL`, `INTERVALO`, `RAZON`).

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Físicas en PostgreSQL:** `tesis_perfil_investigacion`, `tesis_fila_consistencia`, `tesis_variable_investigacion`, `tesis_variable_fila_consistencia`, `tesis_dimension_variable`, `tesis_indicador`.
* **Materialización:** Poblado atómicamente por [`backend/thesis/services/materializadores_pasos/consistencia.py`](../../backend/thesis/services/materializadores_pasos/consistencia.py) al ejecutar `P06`, `P09`, `P10`, `P11` y `P12`.
* **Hidratación de Prompts:** Leído en vivo por [`mcp_server/prompts/hidratacion.py`](../../mcp_server/prompts/hidratacion.py) para inyectar contexto real en los prompts del LLM.
