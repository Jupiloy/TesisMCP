# Explicación de Código: `backend/config/api.py`

## 1. Propósito y ¿Qué hace?
Instancia y configura el framework **Django Ninja** (`NinjaAPI`), que provee la interfaz REST de alto rendimiento con OpenAPI interactivo (/api/v1/docs), serialización y tipado Pydantic. Expone el endpoint de salud `GET /health/` y monta el enrutador de proyectos en `/projects`.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Alternativa Moderna a DRF:** Django Ninja utiliza Pydantic V2 internamente, lo que reduce la sobrecarga de serialización y permite compatibilidad nativa de tipos con el servidor MCP y los contratos de pasos.
* **Documentación Viva:** Genera automáticamente la especificación Swagger/OpenAPI 3.0 para pruebas interactivas de docentes o clientes web.
* **Doble Puerta:** Garantiza que los mismos servicios que consume el servidor MCP puedan ser consumidos por una interfaz web HTTP sin alterar la lógica de negocio.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Crea la instancia `api = NinjaAPI(title="TesisMCP API", version="1.0.0", urls_namespace="api-v1")`.
2. Define el endpoint `api.get("/health/", response={200: HealthResponse})`, que comprueba que la API esté viva retornando `{"status": "ok", "app": "TesisMCP"}`.
3. Importa el enrutador de proyectos `from thesis.api.projects import router as projects_router`.
4. Registra el enrutador bajo el prefijo `/projects` mediante `api.add_router("/projects", projects_router)`.

## 4. Componentes y Funciones Clave
* `api`: Instancia central de `NinjaAPI`.
* `HealthResponse`: Esquema Pydantic que valida la respuesta del endpoint de salud.
* `health_check()`: Controlador HTTP GET para monitoreo y comprobaciones de infraestructura.
* `api.add_router("/projects", projects_router)`: Inclusión modular de endpoints de tesis.

## 5. Relaciones con Otras Capas y Tablas
* **Enrutamiento:** Conectado a [`backend/config/urls.py`](../../backend/config/urls.py) bajo el prefijo `api/v1/`.
* **Endpoints de Dominio:** Consume las rutas definidas en [`backend/thesis/api/projects.py`](../../backend/thesis/api/projects.py).
* **Pruebas:** Verificado directamente por [`backend/thesis/tests/test_health.py`](../../backend/thesis/tests/test_health.py).
