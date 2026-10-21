# Explicación de Código: `backend/config/settings.py`

## 1. Propósito y ¿Qué hace?
Centraliza la configuración de entorno, base de datos, seguridad, aplicaciones instaladas y middleware para el avance evolutivo V1. Conecta de forma aislada a la base de datos PostgreSQL 16 en el puerto `5434` (`tesismcp`), evitando cualquier colisión con el entorno principal (`5432`).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Aislamiento de Entorno:** Para que la evaluación docente y las pruebas de los Capítulos 1 al 3 no interfieran con la base de datos de 24 modelos del proyecto completo, se parametriza una base dedicada en el puerto `5434`.
* **Seguridad Estricta:** Implementa cookies seguras, protección contra sniffing de tipos MIME (`SECURE_CONTENT_TYPE_NOSNIFF`) y autenticación basada en correo mediante el modelo personalizado `Usuario`.
* **Localización Universitaria:** Configura el código de idioma `es-pe` y zona horaria `UTC` para consistencia en marcas de tiempo de auditoría.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Resuelve la ruta raíz `BASE_DIR = Path(__file__).resolve().parent.parent`.
2. Lee `DJANGO_DEBUG` del entorno (por defecto `False` si no se especifica).
3. Parsea `DATABASE_URL` mediante `urllib.parse.urlparse`, extrayendo usuario, contraseña, host y puerto, con valor predeterminado `postgresql://tesismcp:tesismcp_local@127.0.0.1:5434/tesismcp`.
4. Define `DATABASES['default']['TEST']['NAME'] = 'test_tesismcp'` para que `pytest-django` ejecute sobre su propia base de prueba aislada.
5. Registra las aplicaciones nativas de Django (`django.contrib.admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`), extensiones de auditoría (`reversion`) y la aplicación de dominio `thesis.apps.ThesisConfig`.
6. Configura `AUTH_USER_MODEL = 'thesis.Usuario'`, redirigiendo la identidad a un modelo autenticable por email.

## 4. Componentes y Funciones Clave
* `configuracion_postgres(url_bd: str) -> dict`: Función utilitaria que convierte una URL de conexión en el diccionario canónico de conexión para Django PostgreSQL.
* `DATABASES`: Diccionario de configuración de PostgreSQL para producción y entorno de pruebas.
* `AUTH_USER_MODEL = "thesis.Usuario"`: Declaración del modelo de identidad personalizado.
* `INSTALLED_APPS`: Lista limpia que incorpora la app `thesis` y dependencias indispensables.

## 5. Relaciones con Otras Capas y Tablas
* **Base de datos:** Define los parámetros de conexión hacia el contenedor PostgreSQL 16 en `127.0.0.1:5434`.
* **Modelos:** Enlaza el modelo [`Usuario`](../../backend/thesis/models/accounts.py) (`tesis_usuario`).
* **Infraestructura:** Se alinea de forma biunívoca con los puertos publicados en [`compose.yaml`](../../compose.yaml).
