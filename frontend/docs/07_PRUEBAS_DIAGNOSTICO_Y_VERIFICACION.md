# Pruebas, diagnóstico y verificación

## Qué prueban los archivos Node

- `cliente-api.test.mjs`: rutas, cargas canónicas, UUID y adaptación de errores públicos.
- `recorrido-capitulo1.test.mjs`: contratos y transiciones esperadas de P01–P05.
- `recorrido-capitulo2.test.mjs`: contratos y transiciones esperadas de P06–P08.
- `recorrido-capitulo3.test.mjs`: contratos y transiciones esperadas de P09–P12.

Estas pruebas importan funciones puras de `contrato.mjs`. Algunas construyen estados en memoria para comprobar el modelo esperado. No montan React, no controlan un navegador y no prueban por sí solas una escritura real en PostgreSQL.

## Capas de verificación

| Capa | Comando | Detecta principalmente |
|---|---|---|
| Contratos frontend | `pnpm pruebas` | Rutas, cargas y reglas representadas en pruebas Node. |
| Tipos | `pnpm analizar` | Incompatibilidades TypeScript. |
| Lint | `pnpm lint` | Problemas estáticos en `src/`. |
| Compilación | `pnpm compilar` | Fallos del empaquetado de producción. |
| Backend/proyecto V1 | `python3 scripts/verify_project.py` desde `V1/` | Django, migraciones, pruebas, contratos e higiene definidos por V1. |
| Proyecto global | `python3 scripts/verify_project.py` desde la raíz | Puerta integral del repositorio. |

## Diagnóstico rápido

- Si aparece `NO_AUTENTICADO`, comprobar la cookie de sesión y el origen desde el que se abrió el frontend.
- Si falla CSRF, comprobar que Django emitió `csrftoken`, que el proxy se usa y que no se abrió el HTML directamente con `file://`.
- Si aparece `CONFLICTO_VERSION`, recargar el proyecto; no reutilizar una versión anterior.
- Si un paso está bloqueado, revisar las dependencias en la respuesta del proyecto, no forzar el botón desde CSS o React.
- Si el formulario aparece vacío tras abrir un paso, inspeccionar `datos_salida` y la función `salidaPxxInicial` correspondiente.
- Si la compilación funciona pero la API no responde, verificar que Django se ejecuta en `127.0.0.1:8000` para el proxy de desarrollo.

## Criterio de entrega

Una inspección visual no demuestra persistencia ni corrección de contratos. Todo cambio debe terminar con las pruebas focalizadas, análisis, lint, compilación y las puertas deterministas aplicables con código de salida 0.
