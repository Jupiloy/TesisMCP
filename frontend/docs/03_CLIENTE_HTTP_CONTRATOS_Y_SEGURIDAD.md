# Cliente HTTP, contratos y seguridad

## División de responsabilidades

`src/lib/api/contrato.mjs` contiene funciones JavaScript puras para rutas, cargas y errores. Esto permite importarlas directamente desde las pruebas Node. `contrato.d.mts` aporta tipos para ese módulo. `cliente.ts` añade los tipos de dominio y realiza las solicitudes reales con `fetch`.

## Endpoints consumidos

| Operación | Método y ruta |
|---|---|
| Consultar sesión | `GET /api/v1/sesion/actual` |
| Consultar catálogo | `GET /api/v1/metodologia/catalogo` |
| Listar proyectos | `GET /api/v1/proyectos` |
| Crear proyecto | `POST /api/v1/proyectos` |
| Abrir proyecto | `GET /api/v1/proyectos/{id_proyecto}` |
| Guardar paso | `PUT /api/v1/proyectos/{id_proyecto}/pasos/{codigo_paso}` |

La carga canónica del guardado contiene exactamente `contenido_md`, `datos_salida`, `version_esperada` y `clave_idempotencia`.

## Sesión y CSRF

Todas las solicitudes usan `credentials: "same-origin"`, por lo que el navegador envía la cookie de sesión de Django en el mismo origen. En métodos distintos de `GET`, `HEAD` y `OPTIONS`, el cliente lee la cookie `csrftoken` y envía su valor en `X-CSRFToken`.

Esta protección depende también de la configuración y validación del backend. El frontend no guarda credenciales ni tokens de sesión en almacenamiento local.

## Errores públicos

Cuando la respuesta no es exitosa, el cliente intenta leer `codigo`, `mensaje` y `detalle`. Si el cuerpo no tiene JSON válido, construye valores públicos de reserva. `ErrorApi` conserva además el código HTTP.

La pantalla reconoce específicamente:

- HTTP 401, para mostrar el estado sin sesión;
- `CONFLICTO_VERSION`, para evitar una sobrescritura y ofrecer recarga;
- otros errores públicos, que se muestran juntos como código, mensaje y detalle.

## Control de concurrencia e idempotencia

La versión no se incrementa localmente por suposición. Cada guardado usa la `version_estado` recibida y, después del `PUT`, recupera el proyecto completo. Cada intento crea un UUID nuevo mediante la Web Crypto API.

## Límites reales de seguridad

El frontend reduce errores de interacción, pero no sustituye autorización, validación de esquemas ni control de pertenencia en Django. Los atributos HTML como `required`, `minLength` y `maxLength` mejoran la experiencia; el backend continúa siendo la autoridad.

La pantalla sin sesión enlaza actualmente a `/admin/login/?next=/`. Es el acceso administrativo de Django, no un portal de autenticación propio para estudiantes. No debe presentarse como una solución final de inicio de sesión.
