# Explicación de Código: `backend/thesis/management/commands/issue_mcp_token.py`

## 1. Propósito y ¿Qué hace?
Es un comando de consola (`python manage.py issue_mcp_token`) que permite a un administrador o tesista generar un token de autenticación para conectar clientes MCP (como Claude Desktop, Cursor o scripts de prueba) con el backend.

## 2. Justificación Técnica y ¿Por qué lo hace?
El protocolo MCP no utiliza sesiones web basadas en cookies ni cabeceras interactivas tradicionales de navegador. Requiere autenticación mediante un token opaco transmitido por variables de entorno (`TESISMCP_MCP_TOKEN`). Este comando provee una vía determinista y segura para emitir tokens desde la terminal sin comprometer la base de datos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Recibe el argumento `--email` (correo del usuario registrado).
2. Busca el usuario en la tabla `tesis_usuario`. Si no existe, lanza un error de comando.
3. Invoca la función `emitir_token(usuario)` de `thesis.services.mcp_auth`.
4. `emitir_token` genera 48 bytes aleatorios con `secrets.token_urlsafe(48)`, calcula su digest SHA-256 y guarda únicamente el hash en la base de datos.
5. Imprime el token en texto plano en la consola una sola vez para que el usuario lo copie a su configuración.

## 4. Componentes y Funciones Clave
* `Command(BaseCommand)`: Clase que hereda de la infraestructura de comandos de Django.
* `add_arguments(parser)`: Registra el parámetro `--email` obligatorio.
* `handle(*args, **options)`: Orquesta la búsqueda del usuario y la emisión del token.

## 5. Relaciones con Otras Capas y Tablas
* **Servicio:** Delega en [`backend/thesis/services/mcp_auth.py`](../../backend/thesis/services/mcp_auth.py).
* **Modelo:** Inserta registros en [`TokenAccesoMcp`](../../backend/thesis/models/accounts.py) (`tesis_token_acceso_mcp`).
* **Clientes MCP:** El token emitido se consume por [`mcp_server/django_bridge.py`](../../mcp_server/django_bridge.py).
