# Explicación de Código: `backend/thesis/tests/test_extended_steps.py`

## 1. Propósito y ¿Qué hace?
Prueba la **ejecución secuencial integral de los 12 pasos (`P01` a `P12`)** cubriendo los Capítulos 1, 2 y 3. Comprueba la generación del borrador Markdown unificado y valida la **guardia de alcance**, verificando que cualquier intento de ejecutar el paso `P13` (Capítulo 4) sea rechazado deterministamente.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Integración Extremo a Extremo:** Verifica que los 12 contratos Pydantic y sus respectivos materializadores relacionales puedan encadenarse sucesivamente sin errores de clave foránea ni bloqueos de concurrencia.
* **Frontera de Alcance:** Demuestra que la versión reducida V1 respeta su delimitación formal de los primeros 3 capítulos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Ejecuta secuencialmente desde `P01` hasta `P12` incrementando `expected_version` en cada paso.
2. Comprueba que cada paso transicione a `COMPLETED`.
3. Invoca `exportar_borrador_markdown_servicio` y verifica que el texto contenga encabezados de los 3 capítulos.
4. Intenta guardar el paso `P13` y comprueba que se lance un error de validación de catálogo.

## 4. Componentes y Funciones Clave
* Prueba de cadena completa `P01` -> `P12`.
* Prueba de rechazo de `P13`.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** [`steps.py`](../../backend/thesis/services/steps.md) y [`exports.py`](../../backend/thesis/services/exports.md).
* **Catálogo:** [`step_catalogue.py`](../../backend/thesis/step_catalogue.md).
