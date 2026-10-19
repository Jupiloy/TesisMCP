import pytest
from django.test import Client


@pytest.mark.django_db
def test_salud_comprueba_base_datos():
    response = Client().get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
