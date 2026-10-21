# Explicación de Código: `backend/config/urls.py`

## 1. Propósito y ¿Qué hace?
Es el enrutador URL raíz del proyecto web Django. Mapea las solicitudes entrantes hacia tres destinos principales: el endpoint de salud (`/salud/`), el panel de administración (`/admin/`) y la API REST (`/api/v1/`).

## 2. Justificación Técnica y ¿Por qué lo hace?
Centraliza la convención de URLs en un único punto. Mantiene `/salud/` en la raíz para permitir chequeos de disponibilidad inmediatos y aísla la API REST bajo `/api/v1/` para permitir futuros versionados sin romper clientes existentes.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Importa `path` de `django.urls`, `admin` de `django.contrib.admin` y la instancia `api` de `config.api`.
2. Define la vista `salud(request)`, que ejecuta `SELECT 1` en PostgreSQL y retorna `{"estado": "DISPONIBLE"}` o `{"estado": "NO_DISPONIBLE"}`.
3. Compila la lista `urlpatterns`:
   - `path("salud/", salud)`
   - `path("admin/", admin.site.urls)`
   - `path("api/v1/", api.urls)`

## 4. Componentes y Funciones Clave
* `salud(request)`: Vista HTTP de monitoreo con comprobación real de la base de datos.
* `urlpatterns`: Lista canónica de rutas del servidor web.

## 5. Relaciones con Otras Capas y Tablas
* **API:** Mapea la instancia `api.urls` de [`backend/config/api.py`](../../backend/config/api.py).
* **Administración:** Enlaza el sitio `admin.site.urls` configurado en [`backend/thesis/admin.py`](../../backend/thesis/admin.py).
