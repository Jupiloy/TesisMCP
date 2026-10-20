# Explicación de Código: `backend/thesis/services/step_contracts.py`

## 1. Propósito y ¿Qué hace?
Define los **contratos de datos deterministas** para cada uno de los 12 pasos metodológicos (`SalidaP01` a `SalidaP12`), implementados con Pydantic V2. Su clase base `SalidaEstricta` fuerza la regla estricta `extra="forbid"`, impidiendo que un Modelo de Lenguaje (LLM) o cliente externo introduzca campos inventados, no autorizados o mal estructurados.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Cero Tolerancia a Alucinaciones de Estructura:** Los LLMs tienen una tendencia natural a generar campos plausibles pero no solicitados (ej. `cronograma_tentativo`, `costo_estimado`). Si no se configuran contratos estrictos, estos campos espurios contaminan la base de datos o se pierden sin validación.
* **Validación Tipada Temprana:** Al validar el JSON del paso antes de abrir cualquier transacción de base de datos, el sistema evita operaciones de rollback innecesarias y devuelve mensajes de error precisos indicando exactamente qué campo falló.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Declara la clase base `SalidaEstricta(BaseModel)` con:
   ```python
   model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
   ```
2. Modela cada contrato:
   - `SalidaP01`: 5 a 10 temas candidatos con ventajas, desventajas y preselección válida.
   - `SalidaP02`: Ponderación multicriterio de 3 temas con cálculo exacto de puntuaciones.
   - `SalidaP03`: Código ODS validado por regex `^ODS-(0[1-9]|1[0-7]):\d+\.\d+$`.
   - `SalidaP04`: Título estructurado (hasta 20 palabras) con unidad de análisis, lugar y tiempo.
   - `SalidaP05`: Markdown estructurado con mínimo 500 caracteres y 3 párrafos.
   - `SalidaP06`: Planteamiento del problema con 6 bloques (`CA-S-P-CO-CC-PC`).
   - `SalidaP07`: Exactamente 4 justificaciones (`TEORICA`, `PRACTICA`, `METODOLOGICA`, `SOCIAL`).
   - `SalidaP08`: Brecha detectada y estado `PENDING_EVIDENCE`.
   - `SalidaP09`: Objetivos con verbos Bloom permitidos (general y 2 a 4 específicos).
   - `SalidaP10`: Preguntas e hipótesis con signos de interrogación `¿?`.
   - `SalidaP11`: Variables independientes y dependientes con tipo de investigación.
   - `SalidaP12`: Matriz de Operacionalización con dimensiones, indicadores y escala de medición.
3. Centraliza el mapa de despacho en el diccionario `CONTRATOS: dict[str, type[BaseModel]]`.

## 4. Componentes y Funciones Clave
* `SalidaEstricta`: Clase base con prohibición de campos adicionales.
* `CONTRATOS`: Registro de estrategias para resolución en $O(1)$ del validador de cada paso.
* `SalidaP01` a `SalidaP12`: Modelos Pydantic V2 específicos para cada paso.

## 5. Relaciones con Otras Capas y Tablas
* **Servicio:** Invocado por [`backend/thesis/services/steps.py`](../../backend/thesis/services/steps.py) mediante `CONTRATOS[step_code].model_validate(output_data)`.
* **Auditoría:** La puerta [`scripts/verify_project.py`](../../scripts/verify_project.py) prueba inyectar campos espurios para verificar que el contrato los rechace deterministamente.
