from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from thesis.integrations.semantic_scholar import buscar_articulos
from thesis.services.descubrimiento import buscar_semantic_scholar_servicio
from thesis.services.errores import ErrorDominio
from thesis.services.proyectos import crear_proyecto_servicio


def test_resultados_semantic_scholar_son_solo_metadatos():
    carga = {"data": [{
        "paperId": "paper-1", "title": "Artículo de prueba", "year": 2024,
        "authors": [{"name": "Autora"}], "url": "https://example.org/record",
        "externalIds": {"DOI": "10.1234/test"},
        "openAccessPdf": {"url": "https://example.org/test.pdf"},
    }]}
    from unittest.mock import MagicMock
    respuesta = MagicMock()
    respuesta.__enter__.return_value = respuesta
    with patch("thesis.integrations.semantic_scholar.urlopen", return_value=respuesta), \
         patch("thesis.integrations.semantic_scholar.json.load", return_value=carga):
        articulos = buscar_articulos("consulta de prueba")
    assert articulos[0]["titulo"] == "Artículo de prueba"
    assert articulos[0]["nivel_verificacion"] == "SOLO_METADATOS"
    assert articulos[0]["texto_completo_inspeccionado"] is False


@pytest.mark.django_db
def test_busqueda_semantic_scholar_requiere_acceso_proyecto():
    usuarios = get_user_model().objects
    tesista = usuarios.create_user(email="discovery-owner@example.org", password="pass")
    otra = usuarios.create_user(email="discovery-other@example.org", password="pass")
    proyecto = crear_proyecto_servicio(tesista, "Prueba")
    with patch("thesis.services.descubrimiento.buscar_articulos", return_value=[]) as proveedor:
        resultado = buscar_semantic_scholar_servicio(tesista, proyecto.id, "investigación educativa")
    proveedor.assert_called_once()
    assert resultado["texto_completo_inspeccionado"] is False
    with pytest.raises(ErrorDominio) as denegado:
        buscar_semantic_scholar_servicio(otra, proyecto.id, "investigación educativa")
    assert denegado.value.codigo == "NO_ENCONTRADO"
