from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path

from config.api import api


def salud(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"estado": "NO_DISPONIBLE"}, status=503)
    return JsonResponse({"estado": "DISPONIBLE"})

urlpatterns = [
    path("salud/", salud),
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
