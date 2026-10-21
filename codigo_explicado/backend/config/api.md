# Explicación de Código: `backend/config/api.py`

## 1. Propósito y ¿Qué hace?
Instancia y configura **Django Ninja** (`NinjaAPI`), que provee la interfaz REST con OpenAPI interactivo (`/api/v1/docs`), serialización y tipado Pydantic. Monta el enrutador en `/proyectos` y normaliza los errores públicos con `codigo`, `mensaje` y `detalle`.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Alternativa Moderna a DRF:** Django Ninja utiliza Pydantic V2 internamente, lo que reduce la sobrecarga de serialización y permite compatibilidad nativa de tipos con el servidor MCP y los contratos de pasos.
* **Documentación Viva:** Genera automáticamente la especificación Swagger/OpenAPI 3.0 para pruebas interactivas de docentes o clientes web.
* **Doble Puerta:** Garantiza que los mismos servicios que consume el servidor MCP puedan ser consumidos por una interfaz web HTTP sin alterar la lógica de negocio.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Crea la instancia `api = NinjaAPI(title="TesisMCP", version="1.0.0", auth=django_auth)`.
2. Importa `router_proyectos` desde `thesis.api.proyectos` y lo registra bajo `/proyectos`.
3. Define `GET /sesion/actual`, `GET /metodologia/catalogo` y `GET /asesor/panel`.
4. Registra controladores para errores de dominio, autenticación, autorización, validación, HTTP y CSRF con el contrato español uniforme.

## 4. Componentes y Funciones Clave
* `api`: Instancia central de `NinjaAPI`.
* `sesion_actual()`: Devuelve la sesión del usuario autenticado.
* `catalogo_metodologico()`: Expone los 12 pasos y sus esquemas de salida.
* `_respuesta_error_publico()`: Centraliza la forma de los errores HTTP.
* `api.add_router("/proyectos", router_proyectos)`: Incluye los endpoints de tesis.

## 5. Relaciones con Otras Capas y Tablas
* **Enrutamiento:** Conectado a [`backend/config/urls.py`](../../backend/config/urls.py) bajo el prefijo `api/v1/`.
* **Endpoints de Dominio:** Consume las rutas definidas en [`backend/thesis/api/proyectos.py`](../../backend/thesis/api/proyectos.py).
* **Pruebas:** Verificado por [`backend/thesis/tests/test_primer_corte.py`](../../backend/thesis/tests/test_primer_corte.py) y [`test_flujo_academico.py`](../../backend/thesis/tests/test_flujo_academico.py).
