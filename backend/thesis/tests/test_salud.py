import pytest
from django.test import Client


@pytest.mark.django_db
def test_salud_comprueba_base_datos():
    respuesta = Client().get("/salud/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "DISPONIBLE"}
