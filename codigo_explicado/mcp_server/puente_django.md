# Explicación de Código: `mcp_server/puente_django.py`

## 1. Propósito y ¿Qué hace?
Es el **puente de integración** entre el servidor MCP y el framework Django. Configura el entorno de Django (`DJANGO_SETTINGS_MODULE` y `django.setup()`) dentro del proceso MCP, habilita el acceso síncrono controlado al ORM y provee la función `usuario_actual()`, que autentica al usuario a partir de la variable de entorno `TESISMCP_MCP_TOKEN`.

## 2. Justificación Técnica y ¿Por qué lo hace?
El SDK oficial de MCP corre en un bucle de eventos asíncrono (`asyncio`), mientras que muchas operaciones del ORM de Django tradicionalmente son síncronas. Este módulo asegura que Django esté correctamente inicializado antes de procesar cualquier llamada MCP y que las consultas al ORM no arrojen errores de contexto asíncrono.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `configurar_django()`:
   - Añade la carpeta `backend/` a `sys.path`.
   - Establece `DJANGO_SETTINGS_MODULE = "config.settings"`.
   - Habilita `os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"` de forma controlada para el proceso MCP local.
   - Invoca `django.setup()` de forma idempotente (solo si `apps.ready` es `False`).
2. `usuario_actual()`:
   - Lee `os.environ.get("TESISMCP_MCP_TOKEN")`.
   - Invoca `usuario_desde_token(credencial_plana)` de `thesis.services.autenticacion_mcp`.
   - Si no hay token o es inválido, lanza un error de autorización cerrando la operación de forma segura.

## 4. Componentes y Funciones Clave
* `configurar_django()`: Inicializador seguro del entorno Django.
* `usuario_actual()`: Resolvedor de identidad basado en tokens SHA-256.

## 5. Relaciones con Otras Capas y Tablas
* **Servicio:** Consume [`backend/thesis/services/autenticacion_mcp.py`](../../backend/thesis/services/autenticacion_mcp.py).
* **Configuración:** Carga [`backend/config/settings.py`](../../backend/config/settings.py).
