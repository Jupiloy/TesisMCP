# Explicación de Código: `backend/thesis/tests/test_first_slice.py`

## 1. Propósito y ¿Qué hace?
Prueba el **primer corte vertical completo** del sistema: ejecución del paso `P01`, validación del contrato `SalidaP01`, control de concurrencia optimista (`VERSION_CONFLICT`), creación de revisiones inmutables y verificación empírica de que los disparadores PL/pgSQL bloqueen `UPDATE` y `DELETE` en PostgreSQL.

## 2. Justificación Técnica y ¿Por qué lo hace?
Demuestra que la arquitectura desacoplada funciona desde el primer paso metodológico y comprueba a nivel de base de datos que los triggers de inmutabilidad no sean meras declaraciones teóricas, sino barreras efectivas en el motor SQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `test_guardar_paso_p01_exitoso`: Ejecuta `guardar_paso_servicio` con un payload válido y verifica que `ProgresoPaso` quede en `COMPLETED` y `lock_version` pase a 2.
2. `test_guardar_paso_conflicto_version`: Intenta guardar enviando `expected_version=99` y comprueba que se lance `ErrorDominio("VERSION_CONFLICT")`.
3. `test_inmutabilidad_triggers_postgresql`: Intenta ejecutar `RevisionCapitulo.objects.filter(...).update(content="alterado")` y `delete()`, comprobando que PostgreSQL lance `InternalError` o `OperationalError` abortando la transacción.

## 4. Componentes y Funciones Clave
* Pruebas de transacción, concurrencia e inmutabilidad física.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos:** `PerfilInvestigacion`, `RevisionCapitulo`, `ProgresoPaso`.
* **Triggers:** Disparador `tesis_revision_capitulo_solo_anexar` de [`0002_inmutabilidad_espanol.py`](../../backend/thesis/migrations/0002_inmutabilidad_espanol.md).
