import pytest
from django.contrib.auth import get_user_model

from thesis.models import FilaConsistencia, ProgresoPaso
from thesis.services.proyectos import crear_proyecto_servicio


@pytest.fixture
def proyecto_base_con_p08(db):
    usuarios = get_user_model().objects
    tesista = usuarios.create_user(email="extended-owner@example.org", password="pass", display_name="Tesista Extendido")
    proyecto = crear_proyecto_servicio(tesista, "Tesis Completa 32 Pasos")

    # Simular pasos completados P01 a P08 con datos realistas en P04 y P06
    for numero in range(1, 9):
        codigo = f"P{numero:02d}"
        salida = {}
        if codigo == "P04":
            salida = {
                "variables_confirmadas": ["protocolo MCP", "reducción de observaciones"],
                "unidad_analisis_confirmada": "proyectos de tesis",
                "lugar_confirmado": "UTP Piura",
                "periodo_confirmado": 2026,
            }
        elif codigo == "P06":
            salida = {
                "problema_central": "Falta de trazabilidad metodológica en revisiones de tesis",
                "causas_directas": ["Desconexión entre etapas", "Revisión manual dispersa"],
                "efectos_directos": ["Retrasos en entregas", "Inconsistencias de variables"],
                "pregunta_general": "¿Cómo influye el protocolo MCP en la reducción de observaciones?",
                "preguntas_especificas": [
                    "¿Cuál es la tasa de comentarios resueltos por entrega?",
                    "¿Cuál es el tiempo promedio de respuesta del asesor docente?",
                ],
            }
            FilaConsistencia.objects.create(
                project=proyecto,
                ordinal=0,
                question_text=salida["pregunta_general"],
            )
            for indice, pregunta in enumerate(salida["preguntas_especificas"], start=1):
                FilaConsistencia.objects.create(
                    project=proyecto,
                    ordinal=indice,
                    question_text=pregunta,
                )
        ProgresoPaso.objects.create(
            project=proyecto,
            step_code=codigo,
            status=ProgresoPaso.Status.COMPLETADO,
            output_json=salida,
        )
    return tesista, proyecto
