# Explicación de Código: `mcp_server/demostracion/soporte.py`

## 1. Propósito y ¿Qué hace?
Provee utilidades de soporte para la simulación local del servidor MCP: creación de identidades de prueba (estudiante tesista y asesor docente), emisión de tokens opacos SHA-256 e inspección directa de las tablas relacionales en PostgreSQL para verificar los datos persistidos tras la simulación.

## 2. Justificación Técnica y ¿Por qué lo hace?
Aísla la preparación de credenciales y la auditoría SQL de la lógica del guión de simulación, permitiendo verificar empíricamente que las filas en `FilaConsistencia`, `VariableInvestigacion`, dimensiones e indicadores existan físicamente en la base de datos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `_preparar_usuarios_y_tokens()`:
   - Crea o recupera el usuario tesista `u202112345@utp.edu.pe` y el asesor `asesor.sistemas@utp.edu.pe`.
   - Invoca `emitir_token` para ambos usuarios y devuelve sus credenciales.
2. `_inspeccionar_bd_relacional(id_proyecto)`:
   - Consulta PostgreSQL mediante el ORM de Django.
   - Cuenta y extrae: revisiones creadas, filas de consistencia, variables, cruces relacionales, dimensiones, indicadores y eventos de auditoría docente.

## 4. Componentes y Funciones Clave
* `_preparar_usuarios_y_tokens() -> tuple`: Fábrica de identidades y credenciales de prueba.
* `_inspeccionar_bd_relacional(id_proyecto) -> dict`: Auditor relacional posterior a la simulación.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos:** Lee `Usuario`, `PerfilInvestigacion`, `FilaConsistencia`, `VariableInvestigacion`, `RevisionCapitulo`.
* **Consumidor:** Utilizado por [`mcp_server/prueba_local.py`](../prueba_local.md).
