# Explicación de Código: `backend/thesis/api/projects.py`

## 1. Propósito y ¿Qué hace?
Define los controladores HTTP REST con **Django Ninja** para la gestión de proyectos de tesis. Expone endpoints para crear proyectos, consultar el estado del proyecto, guardar pasos metodológicos (`PUT /projects/{id}/steps/{code}`), enviar capítulos a revisión, registrar observaciones y decidir sobre las revisiones.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Doble Puerta de Entrada:** Permite que clientes web tradicionales, aplicaciones móviles o herramientas de pruebas como Postman puedan interactuar con el sistema utilizando exactamente las mismas validaciones y reglas de negocio que utiliza el servidor MCP.
* **Manejo Estandarizado de Errores:** Captura excepciones de dominio (`ErrorDominio`) y las traduce a códigos de estado HTTP apropiados (400 Bad Request, 403 Forbidden, 404 Not Found, 409 Conflict).

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Instancia el enrutador `router = Router(tags=["Proyectos"])`.
2. Define esquemas de entrada y salida con Pydantic V2 (`CrearProyectoIn`, `GuardarPasoIn`, `RespuestaPasoOut`, etc.).
3. Los controladores no contienen lógica SQL directa; autentican al usuario y delegan en la capa de servicios:
   - `PUT /{project_id}/steps/{step_code}` delega en `guardar_paso_servicio`.
   - `POST /{project_id}/chapters/{chapter_number}/submit` delega en `enviar_capitulo_servicio`.
   - `POST /{project_id}/chapters/{chapter_number}/decision` delega en `decidir_capitulo_servicio`.

## 4. Componentes y Funciones Clave
* `guardar_paso_endpoint`: Controlador PUT para ejecutar y persistir pasos metodológicos.
* `enviar_capitulo_endpoint`: Controlador POST para enviar capítulos a revisión docente.
* `decidir_capitulo_endpoint`: Controlador POST para que el asesor apruebe o solicite cambios.

## 5. Relaciones con Otras Capas y Tablas
* **Montaje:** Registrado en [`backend/config/api.py`](../../backend/config/api.py) bajo `/api/v1/projects`.
* **Servicios:** Delega en [`steps.py`](../../backend/thesis/services/steps.py) y [`reviews.py`](../../backend/thesis/services/reviews.py).
