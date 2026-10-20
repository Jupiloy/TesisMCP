# Explicación de Código: `mcp_server/demo/case_data.py`

## 1. Propósito y ¿Qué hace?
Contiene los generadores de **payloads metodológicos simulados** para los 12 pasos (`P01` a `P12`). Construye un caso de tesis realista en ingeniería de sistemas (*Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis en Estudiantes de la UTP Piura, 2026*) con datos válidos que satisfacen el 100% de los contratos Pydantic V2.

## 2. Justificación Técnica y ¿Por qué lo hace?
Permite ejecutar simulaciones End-to-End deterministas y repetibles en entornos de desarrollo y evaluación docente sin depender de llamadas reales a modelos de lenguaje externos, garantizando tiempos de respuesta inmediatos y reproducibilidad matemática.

## 3. Mecanismo Interno y ¿Cómo lo hace?
Provee la función `_construir_payloads_12_pasos()`, que retorna un diccionario donde cada clave es un código de paso (`P01`..`P12`) y su valor contiene:
- `contenido_md`: Documento Markdown formal correspondiente al avance del paso.
- `salida_json`: Diccionario estricto que cumple con los requisitos del validador Pydantic correspondiente.

## 4. Componentes y Funciones Clave
* `_construir_payloads_12_pasos() -> dict`: Fábrica de datos de prueba metodológicos.

## 5. Relaciones con Otras Capas y Tablas
* **Consumidor:** Utilizado por [`mcp_server/test_local.py`](../test_local.md).
* **Contratos:** Valida contra [`backend/thesis/services/step_contracts.py`](../../backend/thesis/services/step_contracts.py).
