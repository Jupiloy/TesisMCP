# Explicación de Código: `backend/thesis/models/accounts.py`

## 1. Propósito y ¿Qué hace?
Define los modelos de seguridad e identidad del sistema:
* `Usuario` (`tesis_usuario`): Modelo de usuario personalizado que utiliza el correo electrónico (`email`) como identificador único de inicio de sesión.
* `TokenAccesoMcp` (`tesis_token_acceso_mcp`): Almacenamiento seguro de credenciales opacas para agentes IA y clientes MCP, persistiendo únicamente el hash SHA-256.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Autenticación por Email:** Los entornos académicos universitarios identifican a sus alumnos y docentes por correos institucionales (`u202112345@utp.edu.pe`), haciendo obsoleto el campo `username` clásico de Django.
* **Seguridad Cero-Texto-Plano:** Guardar tokens de API en texto plano permite que cualquier fuga de base de datos comprometa la identidad de los usuarios. Al guardar exclusivamente `hash_token = sha256(raw_token)`, el sistema previene la suplantación de identidad incluso ante volcados accidentales de SQL.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `Usuario` hereda de `AbstractBaseUser` y `PermissionsMixin`.
   - `email`: `EmailField(unique=True, db_column="correo")`.
   - `USERNAME_FIELD = "email"`.
   - Se gestiona mediante `UsuarioManager`, que normaliza correos y cifra contraseñas con PBKDF2/Argon2.
2. `TokenAccesoMcp`:
   - `hash_token`: `CharField(max_length=64, unique=True, db_column="hash_token")`.
   - `user`: Clave foránea hacia `Usuario` con `on_delete=CASCADE`.
   - `revoked_at`: Marca de tiempo opcional para revocación inmediata.
   - `expires_at`: Marca de tiempo de caducidad.

## 4. Componentes y Funciones Clave
* `Usuario`: Entidad de usuario autenticable con campos en español (`correo`, `esta_activo`, `es_personal`).
* `UsuarioManager`: Gestor de creación de usuarios y superusuarios por correo.
* `TokenAccesoMcp`: Registro seguro de credenciales para el servidor MCP.

## 5. Relaciones con Otras Capas y Tablas
* **Tablas Físicas en PostgreSQL:**
  - `tesis_usuario`: Almacena las cuentas.
  - `tesis_usuario_grupo` y `tesis_usuario_permiso`: Tablas M2M de autorización.
  - `tesis_token_acceso_mcp`: Almacena los hashes de tokens.
* **Servicios:** Consumido por [`backend/thesis/services/mcp_auth.py`](../../backend/thesis/services/mcp_auth.py) y [`mcp_server/django_bridge.py`](../../mcp_server/django_bridge.py).
