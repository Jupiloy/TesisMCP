"""Carga los servicios Django para el transporte MCP stdio local."""

import os
import sys
from pathlib import Path


def configurar_django() -> None:
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    os.environ.setdefault("DJANGO_DEBUG", "1")
    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()


def usuario_actual():
    configurar_django()
    from thesis.services.autenticacion_mcp import usuario_desde_token

    return usuario_desde_token(os.getenv("TESISMCP_MCP_TOKEN", ""))
