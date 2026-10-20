# Explicación de Código: Visión General de la Suite de Pruebas (`backend/thesis/tests/`)

## 1. Propósito y ¿Qué hace?
Centraliza y orquesta las **32 pruebas automatizadas** de la versión reducida V1, ejecutadas con `pytest` y `pytest-django` sobre una base de datos PostgreSQL real (`test_tesismcp_reducido_docente`). Cubre salud de API, corte vertical P01, control de concurrencia optimista, disparadores PL/pgSQL, búsqueda nacional ALICIA, ciclo docente, pasos `P01` a `P12`, materialización del Capítulo 3 y registro de prompts MCP.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Evita Pruebas con Mocks Falsos:** Muchas suites de prueba usan bases de datos en memoria SQLite que no soportan tipos JSONB ni disparadores PL/pgSQL. Al correr contra PostgreSQL real, la suite comprueba que las restricciones de integridad y triggers funcionen exactamente igual que en producción.
* **Red de Seguridad Continua:** Impide regresiones antes de entregar avances al docente o al asesor.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Configurado mediante `pytest.ini` (`DJANGO_SETTINGS_MODULE = config.settings`).
2. Utiliza fixtures compartidos en `conftest.py` para instanciar proyectos y usuarios limpios.
3. Se invoca deterministamente mediante:
   ```bash
   pytest --reuse-db -q
   ```
4. Exige 100% de éxito en las 32 pruebas como condición de salida en la puerta DoD.

## 4. Componentes y Funciones Clave
* 8 módulos de pruebas principales en `backend/thesis/tests/`.
* Submódulo `extended_steps/` con fixtures dedicados para pruebas profundas de consistencia y operacionalización.

## 5. Relaciones con Otras Capas y Tablas
* **Base de datos:** Corre contra `test_tesismcp_reducido_docente` en PostgreSQL puerto 5434.
* **Automatización:** Ejecutado en el paso 4 de [`scripts/verify_project.py`](../scripts/verify_project.md).
