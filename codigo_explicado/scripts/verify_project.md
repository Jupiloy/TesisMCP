# Explicación de Código: `scripts/verify_project.py`

## 1. Propósito y ¿Qué hace?
Es la **Barrera Automática Determinista de Finalización (*Definition of Done Gate*)** del avance evolutivo V1. Ejecuta de forma unificada **7 auditorías técnicas exhaustivas**, exigiendo Código de Salida 0 (`EXIT_CODE_0`) y 100% de éxito como condición obligatoria antes de reportar cualquier entrega técnica o avance.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Prohibición de Cierre sin Evidencia:** Impide que los desarrolladores o agentes de IA declaren tareas como "listas" basándose en inspección visual o memoria abstracta.
* **Auditoría Holística:** Comprueba configuración Django, migraciones, integridad física en PostgreSQL (17 tablas `tesis_*`), la suite completa de 34 pruebas, higiene de archivos (prevención de fugas en `.gitignore` y límite de 250 archivos), consistencia documental y validación adversaria de contratos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
Ejecuta secuencialmente 7 métodos de verificación:
1. `verificar_salud_django`: Ejecuta `manage.py check` (0 errores de sistema).
2. `verificar_migraciones_django`: Ejecuta `makemigrations --check --dry-run` (0 modelos pendientes).
3. `verificar_esquema_fisico_espanol`: Se conecta a `information_schema` y `pg_catalog` en PostgreSQL para comprobar que existan exactamente las 17 tablas `tesis_*`, sus columnas en español, la función `tesis_rechazar_cambio_historial` y los dos triggers de inmutabilidad.
4. `verificar_suite_pytest`: Ejecuta `pytest --reuse-db -q` exigiendo 34 pruebas aprobadas al 100%.
5. `verificar_higiene_repositorio`: Revisa `.gitignore`, cachés, archivos temporales, que no se superen los 250 archivos y que el `Dockerfile` no copie fuentes inexistentes.
6. `verificar_consistencia_documentacion_codigo`: Comprueba matemáticamente que la documentación cite las cifras reales (15 modelos, 2 migraciones, 12 pasos, 17 herramientas MCP, 15 prompts) y que existan 0 enlaces Markdown rotos.
7. `verificar_auditoria_adversaria_contratos`: Intenta inyectar un campo espurio no autorizado en `SalidaP01` para comprobar que `extra="forbid"` esté activo, y comprueba la ausencia de datos simulados/mocks en producción.

## 4. Componentes y Funciones Clave
* `SuiteVerificacion`: Clase orquestadora de auditorías.
* `ejecutar_comando(...)`: Subproceso controlado con captura de salidas y tiempos.
* Veredicto formal: `[APROBADO_CON_EVIDENCIA / EXIT_CODE_0]`.

## 5. Relaciones con Otras Capas y Tablas
* Audita todo el repositorio `V1/`, su base de datos PostgreSQL en el puerto `5434` y los contratos Pydantic.
