from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from thesis.integrations.semantic_scholar import buscar_articulos
from thesis.services.discovery import buscar_semantic_scholar_servicio
from thesis.services.errors import ErrorDominio
from thesis.services.projects import crear_proyecto_servicio


def test_resultados_semantic_scholar_son_solo_metadatos():
    payload = {"data": [{
        "paperId": "paper-1", "title": "Artículo de prueba", "year": 2024,
        "authors": [{"name": "Autora"}], "url": "https://example.org/record",
        "externalIds": {"DOI": "10.1234/test"},
        "openAccessPdf": {"url": "https://example.org/test.pdf"},
    }]}
    from unittest.mock import MagicMock
    response = MagicMock()
    response.__enter__.return_value = response
    with patch("thesis.integrations.semantic_scholar.urlopen", return_value=response), \
         patch("thesis.integrations.semantic_scholar.json.load", return_value=payload):
        papers = buscar_articulos("consulta de prueba")
    assert papers[0]["title"] == "Artículo de prueba"
    assert papers[0]["verification_level"] == "METADATA_ONLY"
    assert papers[0]["full_text_inspected"] is False


@pytest.mark.django_db
def test_busqueda_semantic_scholar_requiere_acceso_proyecto():
    users = get_user_model().objects
    owner = users.create_user(email="discovery-owner@example.org", password="pass")
    other = users.create_user(email="discovery-other@example.org", password="pass")
    project = crear_proyecto_servicio(owner, "Prueba")
    with patch("thesis.services.discovery.buscar_articulos", return_value=[]) as provider:
        result = buscar_semantic_scholar_servicio(owner, project.id, "investigación educativa")
    provider.assert_called_once()
    assert result["full_text_inspected"] is False
    with pytest.raises(ErrorDominio) as denied:
        buscar_semantic_scholar_servicio(other, project.id, "investigación educativa")
    assert denied.value.code == "NOT_FOUND"
