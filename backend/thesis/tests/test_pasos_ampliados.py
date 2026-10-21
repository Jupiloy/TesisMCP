import pytest
from pydantic import ValidationError

from thesis.services.contratos_pasos import CONTRATOS, SalidaP04, SalidaP09, SalidaP10
from thesis.services.pasos import PASOS_CAPITULO
from thesis.catalogo_pasos import CATALOGO_PASOS


def test_catalogo_12_pasos_y_3_capitulos():
    assert len(CONTRATOS) == 12
    assert set(PASOS_CAPITULO.keys()) == {1, 2, 3}
    total_pasos_capitulos = sum(len(pasos) for pasos in PASOS_CAPITULO.values())
    assert total_pasos_capitulos == 12
    assert set(CATALOGO_PASOS) == set(CONTRATOS)
    assert {codigo: capitulo for capitulo, codigos in PASOS_CAPITULO.items() for codigo in codigos} == {
        codigo: informacion["capitulo"] for codigo, informacion in CATALOGO_PASOS.items()
    }
    for numero in range(1, 13):
        codigo = f"P{numero:02d}"
        assert codigo in CONTRATOS
    assert "P13" not in CONTRATOS
    assert "P13" not in CATALOGO_PASOS


def test_validador_titulo_p04_limite_20_palabras_y_componentes():
    titulo = "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis en Estudiantes de la UTP Piura, 2026"
    p04 = SalidaP04.model_validate({
        "titulo_oficial": titulo,
        "conteo_palabras": 18,
        "variables_confirmadas": ["Protocolo MCP", "Formulación Metodológica de Tesis"],
        "unidad_analisis_confirmada": "Estudiantes",
        "lugar_confirmado": "UTP Piura",
        "periodo_confirmado": 2026,
    })
    assert p04.conteo_palabras == 18

    with pytest.raises(ValidationError):
        SalidaP04.model_validate({
            "titulo_oficial": titulo,
            "conteo_palabras": 15,  # No coincide con 18
            "variables_confirmadas": ["Protocolo MCP"],
            "unidad_analisis_confirmada": "Estudiantes",
            "lugar_confirmado": "UTP Piura",
            "periodo_confirmado": 2026,
        })


def test_validador_bloom_p09_exitoso_y_fallido():
    valido = {
        "objetivo_general": "Determinar el impacto de la herramienta digital en el rendimiento académico",
        "objetivos_especificos": [
            "Analizar el nivel inicial de competencias de los estudiantes",
            "Evaluar la percepción de los docentes sobre la plataforma",
        ],
    }
    salida = SalidaP09.model_validate(valido)
    assert salida.objetivo_general.startswith("Determinar")

    invalido = {
        "objetivo_general": "El presente estudio busca conocer el impacto de la herramienta",
        "objetivos_especificos": [
            "Analizar el nivel inicial",
            "Evaluar la percepción",
        ],
    }
    with pytest.raises(ValidationError) as error:
        SalidaP09.model_validate(invalido)
    assert "verbo de Bloom válido" in str(error.value)


def test_validador_preguntas_p10_con_signos():
    valido = {
        "pregunta_general": "¿De qué manera influye la arquitectura MCP en la trazabilidad de tesis?",
        "preguntas_especificas": [
            "¿Cuál es el nivel de adopción del protocolo en el equipo?",
            "¿Cómo se relacionan los contratos de validación con la reducción de alucinaciones?",
        ],
    }
    resultado = SalidaP10.model_validate(valido)
    assert resultado.pregunta_general.startswith("¿")

    sin_signos = {
        "pregunta_general": "De qué manera influye la arquitectura MCP",
        "preguntas_especificas": ["¿Cuál es el nivel de adopción?", "¿Cómo se relacionan?"],
    }
    with pytest.raises(ValidationError):
        SalidaP10.model_validate(sin_signos)
