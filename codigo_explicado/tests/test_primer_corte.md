# Explicación de Código: `backend/thesis/tests/test_primer_corte.py`

## 1. Propósito y ¿Qué hace?
Prueba el **primer corte vertical completo** del sistema: sesión y CSRF, contrato OpenAPI en español, control de concurrencia optimista (`CONFLICTO_VERSION`), identidad MCP y forma pública de errores MCP.

## 2. Justificación Técnica y ¿Por qué lo hace?
Demuestra que la arquitectura desacoplada funciona desde el primer paso metodológico y comprueba a nivel de base de datos que los triggers de inmutabilidad no sean meras declaraciones teóricas, sino barreras efectivas en el motor SQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `test_api_requiere_sesion_y_csrf`: verifica rutas canónicas, autenticación, CSRF y errores con `codigo`, `mensaje`, `detalle`.
2. `test_aislamiento_proyecto_y_conflicto_version`: intenta guardar con una `version_esperada` obsoleta y comprueba `ErrorDominio("CONFLICTO_VERSION")`.
3. `test_inmutabilidad_triggers_postgresql`: Intenta ejecutar `RevisionCapitulo.objects.filter(...).update(content="alterado")` y `delete()`, comprobando que PostgreSQL lance `InternalError` o `OperationalError` abortando la transacción.

## 4. Componentes y Funciones Clave
* Pruebas de transacción, concurrencia e inmutabilidad física.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos:** `PerfilInvestigacion`, `RevisionCapitulo`, `ProgresoPaso`.
* **Triggers:** Disparador `tesis_revision_capitulo_solo_anexar` de [`0002_integridad_esquema.py`](../../backend/thesis/migrations/0002_integridad_esquema.md).
