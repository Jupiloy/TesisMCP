from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from thesis.integrations.alicia import buscar_tesis_alicia
from thesis.services.descubrimiento_peru import _clasificar_localidad, buscar_antecedentes_peru_servicio
from thesis.services.errores import ErrorDominio
from thesis.services.geografia import resolver_alcance_geografico
from thesis.services.proyectos import crear_proyecto_servicio


def test_resolucion_geografica_dinamica():
    # Caso 1: Región directa
    alcance_piura = resolver_alcance_geografico("Piura, Perú")
    assert alcance_piura.region == "Piura"
    assert "UDEP" in alcance_piura.instituciones_locales
    assert "sullana" in alcance_piura.palabras_coincidencia

    # Caso 2: Provincia/Distrito perteneciente a la región
    alcance_sullana = resolver_alcance_geografico("Provincia de Sullana")
    assert alcance_sullana.region == "Piura"

    # Caso 3: Otra región peruana
    alcance_arequipa = resolver_alcance_geografico("Arequipa")
    assert alcance_arequipa.region == "Arequipa"
    assert "UNSA" in alcance_arequipa.instituciones_locales

    # Caso 4: Lugar no indexado previamente (fallback dinámico sin fallos)
    alcance_personalizado = resolver_alcance_geografico("Chachapoyas")
    assert alcance_personalizado.region == "Chachapoyas"
    assert "chachapoyas" in alcance_personalizado.palabras_coincidencia

    # Caso 5: Lugar vacío
    alcance_vacio = resolver_alcance_geografico(None)
    assert alcance_vacio.region == "Perú"
    assert alcance_vacio.palabras_coincidencia == []


def test_localidad_requiere_terminos_geograficos_completos():
    lima = resolver_alcance_geografico("Lima")
    registro_piura = {"titulo": "Gestión académica en Piura", "institucion": "Universidad Nacional de Piura"}
    assert _clasificar_localidad(registro_piura, lima)[0] is False
    assert _clasificar_localidad({"titulo": "Estudio realizado en Perú", "institucion": "Universidad de Piura"},
                             resolver_alcance_geografico(None))[0] is False


def test_normalizacion_alicia_es_solo_metadatos():
    carga_simulada = {
        "status": "OK",
        "resultCount": 1,
        "records": [{
            "id": "alicia-101",
            "title": "Sistema web para la gestión de proyectos de tesis en Piura",
            "authors": {"primary": {"García, Juan": {"role": ["author"]}}, "secondary": []},
            "publicationDates": ["2024"],
            "thesisDegreeGrantor": ["Universidad Nacional de Piura"],
            "urls": [{"url": "https://hdl.handle.net/11042/1234", "desc": "Repositorio"}],
            "dcDescriptionAbstract": ["Resumen de la tesis en la ciudad de Piura."],
        }],
    }
    respuesta_simulada = MagicMock()
    respuesta_simulada.__enter__.return_value = respuesta_simulada
    with patch("thesis.integrations.alicia.urlopen", return_value=respuesta_simulada), \
         patch("thesis.integrations.alicia.json.load", return_value=carga_simulada):
        resultados = buscar_tesis_alicia("sistema web tesis")

    assert len(resultados) == 1
    documento = resultados[0]
    assert documento["titulo"] == "Sistema web para la gestión de proyectos de tesis en Piura"
    assert documento["autores"] == ["García, Juan"]
    assert documento["anio_publicacion"] == 2024
    assert documento["url_handle"] == "https://hdl.handle.net/11042/1234"
    assert documento["nivel_verificacion"] == "SOLO_METADATOS"
    assert documento["texto_completo_inspeccionado"] is False


def test_alicia_no_inventa_institucion_ni_mezcla_asesores_autores():
    from thesis.integrations.alicia import _normalizar_registro_alicia

    resultado = _normalizar_registro_alicia({
        "id": "registro-1",
        "title": "Tesis de ejemplo",
        "authors": {"primary": {"Autora Real": {}}, "secondary": {"Asesor": {}}},
        "dcDateIssued": ["2024-05-10"],
    })
    assert resultado["autores"] == ["Autora Real"]
    assert resultado["anio_publicacion"] == 2024
    assert resultado["institucion"] is None


@pytest.mark.django_db
def test_busqueda_antecedentes_peru_clasificacion_y_filtros():
    usuarios = get_user_model().objects
    tesista = usuarios.create_user(email="tesista-peru@example.org", password="pass")
    intruso = usuarios.create_user(email="intruso@example.org", password="pass")
    proyecto = crear_proyecto_servicio(tesista, "Tesis Piura")

    # Configurar el lugar del perfil como Piura
    perfil = proyecto.profile
    perfil.place = "Piura, Perú"
    perfil.save(update_fields=["place"])

    registros_alicia_simulados = [
        {
            "origen_fuente": "ALICIA_CONCYTEC",
            "id_registro": "1",
            "titulo": "Repositorio de lecciones de ingeniería",
            "autores": ["Cáceres, D."],
            "anio_publicacion": 2025,
            "institucion": "Universidad de Piura",
            "url_handle": "https://hdl.handle.net/11042/7457",
            "resumen": "Estudio desarrollado en el Campus Piura.",
            "nivel_verificacion": "SOLO_METADATOS",
            "texto_completo_inspeccionado": False,
        },
        {
            "origen_fuente": "ALICIA_CONCYTEC",
            "id_registro": "2",
            "titulo": "Control de inventario en planta pesquera de Paita",
            "autores": ["López, M."],
            "anio_publicacion": 2024,
            "institucion": "Universidad Tecnológica del Perú",
            "url_handle": "https://repositorio.utp.edu.pe/handle/20.500.12867/999",
            "resumen": "Aplicado a una empresa de la provincia de Paita.",
            "nivel_verificacion": "SOLO_METADATOS",
            "texto_completo_inspeccionado": False,
        },
        {
            "origen_fuente": "ALICIA_CONCYTEC",
            "id_registro": "3",
            "titulo": "Arquitectura de microservicios bancarios en Lima",
            "autores": ["Rojas, E."],
            "anio_publicacion": 2023,
            "institucion": "Pontificia Universidad Católica del Perú",
            "url_handle": "https://tesis.pucp.edu.pe/repositorio/handle/20.500.12404/555",
            "resumen": "Caso de estudio en San Isidro, Lima.",
            "nivel_verificacion": "SOLO_METADATOS",
            "texto_completo_inspeccionado": False,
        },
    ]

    with patch("thesis.services.descubrimiento_peru.buscar_tesis_alicia", return_value=registros_alicia_simulados), \
         patch("thesis.services.descubrimiento_peru.buscar_articulos_afiliacion_peru", return_value=[]):

        # 1. Búsqueda con scope_filter="todos": debe incluir ambos y priorizar locales
        datos_todos = buscar_antecedentes_peru_servicio(tesista, proyecto.id, "ingeniería de sistemas", filtro_alcance="todos")
        resultados_todos = datos_todos["resultados"]
        assert len(resultados_todos) == 3
        assert resultados_todos[0]["es_local"] is True
        assert "LOCAL_POR_INSTITUCION" in resultados_todos[0]["justificacion_local"]
        assert resultados_todos[1]["es_local"] is True
        assert "LOCAL_POR_OBJETO_ESTUDIO" in resultados_todos[1]["justificacion_local"]
        assert resultados_todos[2]["es_local"] is False
        assert "NACIONAL" in resultados_todos[2]["justificacion_local"]

        # 2. Búsqueda con scope_filter="locales": solo los 2 de Piura
        datos_locales = buscar_antecedentes_peru_servicio(tesista, proyecto.id, "ingeniería de sistemas", filtro_alcance="locales")
        resultados_locales = datos_locales["resultados"]
        assert len(resultados_locales) == 2
        assert all(elemento["es_local"] is True for elemento in resultados_locales)

        # 3. Búsqueda con scope_filter="nacionales": solo el de Lima (no local)
        datos_nacionales = buscar_antecedentes_peru_servicio(tesista, proyecto.id, "ingeniería de sistemas", filtro_alcance="nacionales")
        resultados_nacionales = datos_nacionales["resultados"]
        assert len(resultados_nacionales) == 1
        assert resultados_nacionales[0]["es_local"] is False

    # 4. Control de acceso: intruso rechazado con NO_ENCONTRADO
    with pytest.raises(ErrorDominio) as denegado:
        buscar_antecedentes_peru_servicio(intruso, proyecto.id, "ingeniería de sistemas")
    assert denegado.value.codigo == "NO_ENCONTRADO"


@pytest.mark.django_db
def test_busqueda_reporta_caidas_proveedores():
    tesista = get_user_model().objects.create_user(email="busqueda@example.org", password="pass")
    proyecto = crear_proyecto_servicio(tesista, "Búsqueda Piura")
    proyecto.profile.place = "Piura"
    proyecto.profile.save(update_fields=["place"])
    no_disponible = ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "Proveedor caído")
    with patch("thesis.services.descubrimiento_peru.buscar_tesis_alicia", side_effect=no_disponible), \
         patch("thesis.services.descubrimiento_peru.buscar_articulos_afiliacion_peru", side_effect=no_disponible):
        with pytest.raises(ErrorDominio) as exc:
            buscar_antecedentes_peru_servicio(tesista, proyecto.id, "tesis")
    assert exc.value.codigo == "BUSQUEDA_NO_DISPONIBLE"


def test_articulos_openalex_no_afirman_revision_pares():
    from thesis.integrations.articulos_peru import buscar_articulos_afiliacion_peru

    carga = {"results": [
        {"id": "W1", "title": "Artículo", "type": "article", "authorships": []},
        {"id": "W2", "title": "Libro", "type": "book", "authorships": []},
    ]}
    respuesta_simulada = MagicMock()
    respuesta_simulada.__enter__.return_value = respuesta_simulada
    with patch("thesis.integrations.articulos_peru.urlopen", return_value=respuesta_simulada), \
         patch("thesis.integrations.articulos_peru.json.load", return_value=carga):
        resultado = buscar_articulos_afiliacion_peru("tesis")
    assert len(resultado) == 1
    assert resultado[0]["origen_fuente"] == "ARTICULO_CON_FILIACION_PERUANA"
    assert resultado[0]["revision_pares_verificada"] is False
