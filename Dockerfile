FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng \
    ghostscript pngquant unpaper \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt /app/
RUN python -m pip install --no-cache-dir -r requirements-backend.txt
COPY backend /app/backend
COPY mcp_server /app/mcp_server
COPY core /app/core

RUN DJANGO_DEBUG=1 python backend/manage.py collectstatic --noinput
RUN useradd --system --create-home --uid 10001 tesismcp \
    && mkdir -p /app/var/media /app/var/models \
    && chown -R tesismcp:tesismcp /app
USER tesismcp
EXPOSE 8000
CMD ["gunicorn", "--chdir", "backend", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
