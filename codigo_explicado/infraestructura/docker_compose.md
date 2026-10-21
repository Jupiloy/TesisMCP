# Explicación de Código: Infraestructura y Contenedores (`compose.yaml` y `Dockerfile`)

## 1. Propósito y ¿Qué hace?
Define la infraestructura de despliegue contenerizado y aislamiento para el avance evolutivo V1:
* `compose.yaml`: Orquesta los servicios `postgres` (PostgreSQL 16 publicado en el puerto aislado `127.0.0.1:5434`), `backend` (Django Ninja en el puerto `8000`) y `mcp` (perfil con transporte `stdio`).
* `Dockerfile`: Imagen de contenedor ligera basada en `python:3.14-slim`, configurando dependencias de producción y usuario sin privilegios.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Aislamiento de Puerto 5434:** El entorno principal de TesisMCP utiliza habitualmente el puerto `5432`. Asignar el puerto `5434` al avance V1 permite que ambos entornos coexistan en la misma máquina sin conflictos de red ni sobreescritura de volúmenes.
* **Reproducibilidad Inmediata:** Permite a evaluadores o docentes levantar todo el sistema con un único comando (`podman compose up -d` o `docker compose up -d`).

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `compose.yaml`:
   - Servicio `postgres`: Imagen `postgres:16`, variables `POSTGRES_DB=tesismcp`, puerto `"127.0.0.1:5434:5432"` y volumen persistente `postgres_data`.
   - Servicio `backend`: Compila desde `Dockerfile`, expone `"8000:8000"`, configura `DATABASE_URL` y ejecuta `gunicorn config.wsgi:application`.
   - Servicio `mcp`: Perfil opcional `profiles: ["mcp"]` para invocar el servidor `python mcp_server/server.py` sobre transporte estándar.
2. `Dockerfile`:
   - Imagen base `python:3.14-slim`.
   - Instala `requirements-backend.txt`.
   - Copia el código fuente y expone el puerto 8000.

## 4. Componentes y Funciones Clave
* Servicios `postgres`, `backend` y `mcp`.
* Volumen aislado `postgres_data`.

## 5. Relaciones con Otras Capas y Tablas
* **Configuración:** Suministra la base de datos a [`backend/config/settings.py`](../../backend/config/settings.md).
* **Verificación:** Auditado por [`scripts/verify_project.py`](../scripts/verify_project.md).
