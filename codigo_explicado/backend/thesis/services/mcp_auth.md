# Explicación de Código: `backend/thesis/services/mcp_auth.py`

## 1. Propósito y ¿Qué hace?
Implementa el sistema de **autenticación criptográfica por tokens opacos** para el servidor MCP. Provee las funciones para emitir nuevos tokens (`emitir_token`), calcular su resumen SHA-256 y autenticar usuarios a partir de la variable de entorno `TESISMCP_MCP_TOKEN`.

## 2. Justificación Técnica y ¿Por qué lo hace?
El protocolo MCP carece de un flujo interactivo de login con redirecciones OAuth o cookies de sesión. Requiere una credencial estática de alta entropía que identifique de forma unívoca al actor (tesista o asesor). Guardar solo el SHA-256 en PostgreSQL asegura que las credenciales no queden expuestas en volcados de datos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `emitir_token(usuario, dias_expiracion=30)`:
   - Genera una cadena aleatoria segura con `secrets.token_urlsafe(48)` (entropía criptográfica).
   - Calcula su hash hexadecimal con `hashlib.sha256(raw_token.encode()).hexdigest()`.
   - Almacena en `TokenAccesoMcp` el hash, el usuario y la fecha de expiración.
   - Retorna el token en texto plano (única vez que existe en memoria).
2. `usuario_desde_token(token_plano)`:
   - Si no se proporciona token, retorna `None`.
   - Calcula `hashlib.sha256(token_plano.encode()).hexdigest()`.
   - Busca en `TokenAccesoMcp` coincidencia de hash, verificando que el usuario esté activo (`is_active=True`), no haya sido revocado (`revoked_at__isnull=True`) y no haya expirado.

## 4. Componentes y Funciones Clave
* `emitir_token(user, days=30) -> str`: Genera y persiste un token retornando el valor plano.
* `usuario_desde_token(raw_token: str) -> Optional[Usuario]`: Resuelve la identidad a partir del token.

## 5. Relaciones con Otras Capas y Tablas
* **Tabla:** `tesis_token_acceso_mcp` en PostgreSQL.
* **CLI:** Invocado por el comando de administración [`issue_mcp_token.py`](../../backend/thesis/management/commands/issue_mcp_token.py).
* **Puente MCP:** Utilizado en cada llamada de herramienta por [`mcp_server/django_bridge.py`](../../mcp_server/django_bridge.py).
