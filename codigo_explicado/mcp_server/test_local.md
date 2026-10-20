# Explicación de Código: `mcp_server/test_local.py`

## 1. Propósito y ¿Qué hace?
Es el script de **simulación End-to-End interactiva** del servidor MCP. Ejecuta una tesis completa de principio a fin sin requerir un cliente externo: levanta la instancia de `MCPServer`, crea un tesista y un asesor con tokens SHA-256, crea el proyecto, ejecuta secuencialmente los 12 pasos (`P01` a `P12`), demuestra el rechazo controlado del paso fuera de alcance `P13`, ancla una observación docente, comprueba el bloqueo de aprobación mientras la observación esté abierta, la resuelve y aprueba los Capítulos 1, 2 y 3.

## 2. Justificación Técnica y ¿Por qué lo hace?
Provee un mecanismo reproducible y observable para que docentes, evaluadores y desarrolladores verifiquen el funcionamiento íntegro de la plataforma en vivo mediante un único comando (`python mcp_server/test_local.py`), mostrando en consola el avance de `lock_version`, las revisiones inmutables y las entidades creadas en PostgreSQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Prepara las identidades con `_preparar_usuarios_y_tokens()` (emitiendo tokens para `u202112345@utp.edu.pe` y `asesor.sistemas@utp.edu.pe`).
2. Configura `TESISMCP_MCP_TOKEN` en el entorno como el tesista y llama a `crear_proyecto`.
3. Asigna al asesor mediante `asignar_asesor`.
4. Itera sobre los 12 payloads metodológicos provistos por `case_data.py`, invocando `guardar_paso` para cada uno y mostrando la versión optimista (`lock_version = 1..12`).
5. Intenta invocar `guardar_paso` con `P13` y captura la excepción `VALIDATION_ERROR`.
6. Cambia `TESISMCP_MCP_TOKEN` al asesor: ancla una observación en el Capítulo 3 con `observar_fragmento`.
7. Intenta aprobar con `decidir_capitulo(APPROVE)` y captura el error `ADVISOR_UNRESOLVED_COMMENTS`.
8. Resuelve el comentario con `resolver_observacion` y aprueba los Capítulos 1, 2 y 3.
9. Inspecciona la base de datos con `_inspeccionar_bd_relacional()` e imprime un resumen consolidado.

## 4. Componentes y Funciones Clave
* `probar_servidor_mcp()`: Función asíncrona principal de la simulación.
* `_desenvolver(tool_res)`: Función de deserialización del resultado de la herramienta MCP.

## 5. Relaciones con Otras Capas y Tablas
* **Servidor MCP:** Invoca directamente la instancia `app` de [`server.py`](./server.md).
* **Datos:** Consume [`case_data.py`](./demo/case_data.md) y [`support.py`](./demo/support.md).
