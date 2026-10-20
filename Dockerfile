# TesisMCP — Imagen de Contenedor para Backend y Servidor MCP
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements-backend.txt /app/
RUN python -m pip install --no-cache-dir -r requirements-backend.txt
COPY backend /app/backend
COPY mcp_server /app/mcp_server

RUN DJANGO_DEBUG=1 python backend/manage.py collectstatic --noinput
RUN useradd --system --create-home --uid 10001 tesismcp \
    && mkdir -p /app/var/media /app/var/models \
    && chown -R tesismcp:tesismcp /app
USER tesismcp
EXPOSE 8000
CMD ["gunicorn", "--chdir", "backend", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
