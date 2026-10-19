from uuid import uuid4

import pytest

from thesis.models import Capitulo, FilaConsistencia, VariableFilaConsistencia, Indicador, VariableInvestigacion, DimensionVariable
from thesis.services.errors import ErrorDominio
from thesis.services.projects import obtener_estado_proyecto
from thesis.services.steps import guardar_paso_servicio, enviar_capitulo_servicio


def test_flujo_completo_capitulo_3_persistencia_relacional_y_consistencia(proyecto_base_con_p08):
    owner, project = proyecto_base_con_p08

    # 1. Fallo si P09 tiene distinto número de objetivos específicos que preguntas específicas en P06 (2)
    with pytest.raises(ErrorDominio) as exc_mismatch:
        guardar_paso_servicio(
            actor=owner,
            project_id=project.id,
            step_code="P09",
            content_md="# Objetivos con desajuste",
            output_data={
                "objetivo_general": "Determinar la influencia del protocolo MCP en la reducción de observaciones",
                "objetivos_especificos": [
                    "Analizar la tasa de comentarios resueltos en cada entrega",
                    "Evaluar el tiempo promedio de respuesta del asesor docente",
                    "Comparar la satisfacción estudiantil entre ciclos",
                ],
            },
            expected_version=0,
            idempotency_key=str(uuid4()),
        )
    assert exc_mismatch.value.code == "RULE_CONSISTENCY_MISMATCH"

    # 2. Guardado exitoso de P09
    res_p09 = guardar_paso_servicio(
        actor=owner,
        project_id=project.id,
        step_code="P09",
        content_md="# Capítulo 3: Objetivos\n\nEl objetivo general es determinar la influencia...",
        output_data={
            "objetivo_general": "Determinar la influencia del protocolo MCP en la reducción de observaciones",
            "objetivos_especificos": [
                "Analizar la tasa de comentarios resueltos en cada entrega",
                "Evaluar el tiempo promedio de respuesta del asesor docente",
            ],
        },
        expected_version=0,
        idempotency_key=str(uuid4()),
    )
    assert res_p09["chapter_no"] == 3
    assert res_p09["state_version"] == 1
    assert FilaConsistencia.objects.get(project=project, ordinal=0).objective_text.startswith("Determinar")

    # 3. Guardado exitoso de P10
    res_p10 = guardar_paso_servicio(
        actor=owner,
        project_id=project.id,
        step_code="P10",
        content_md="# Preguntas Consolidadas",
        output_data={
            "pregunta_general": "¿De qué manera influye el protocolo MCP en la reducción de observaciones?",
            "preguntas_especificas": [
                "¿Cuál es la tasa de comentarios resueltos en cada entrega?",
                "¿Cuál es el tiempo promedio de respuesta del asesor docente?",
            ],
        },
        expected_version=1,
        idempotency_key=str(uuid4()),
    )
    assert res_p10["state_version"] == 2

    # 4. Guardado exitoso de P11 (Hipótesis y Variables relacionales)
    res_p11 = guardar_paso_servicio(
        actor=owner,
        project_id=project.id,
        step_code="P11",
        content_md="# Hipótesis y Variables",
        output_data={
            "tipo_investigacion": "APLICADA",
            "hipotesis_general": "El protocolo MCP influye significativamente en la reducción de observaciones",
            "hipotesis_especificas": [
                "La tasa de comentarios resueltos incrementa con la validación por contratos",
                "El tiempo promedio de respuesta del asesor disminuye mediante anclajes de texto",
            ],
            "variable_independiente": "protocolo MCP",
            "variable_dependiente": "reducción de observaciones",
        },
        expected_version=2,
        idempotency_key=str(uuid4()),
    )
    assert res_p11["state_version"] == 3
    assert VariableInvestigacion.objects.filter(project=project).count() == 2
    assert VariableFilaConsistencia.objects.filter(consistency_row__project=project).count() == 6  # 3 filas x 2 variables

    # 5. Guardado exitoso de P12 (Matriz de Operacionalización -> Dimensiones e Indicadores)
    res_p12 = guardar_paso_servicio(
        actor=owner,
        project_id=project.id,
        step_code="P12",
        content_md="# Matriz de Operacionalización de Variables",
        output_data={
            "matriz_operacionalizacion": [
                {
                    "variable": "protocolo MCP",
                    "definicion_conceptual": "Estándar de comunicación entre modelos de lenguaje y servidores de contexto.",
                    "definicion_operacional": "Medición mediante registros de llamadas a herramientas y validación de contratos.",
                    "dimensiones": ["Validación de Esquemas", "Trazabilidad de Estado"],
                    "indicadores": ["Tasa de contratos válidos", "Porcentaje de bloqueos por prerrequisito"],
                    "escala_medicion": "RAZON",
                },
                {
                    "variable": "reducción de observaciones",
                    "definicion_conceptual": "Disminución de correcciones metodológicas solicitadas por el asesor.",
                    "definicion_operacional": "Conteo de eventos de revisión e incidencias abiertas por capítulo.",
                    "dimensiones": ["Consistencia Metodológica", "Velocidad de Revisión"],
                    "indicadores": ["Número de observaciones por entrega", "Horas promedio hasta aprobación"],
                    "escala_medicion": "RAZON",
                },
            ]
        },
        expected_version=3,
        idempotency_key=str(uuid4()),
    )
    assert res_p12["state_version"] == 4
    assert DimensionVariable.objects.filter(variable__project=project).count() == 4
    assert Indicador.objects.filter(dimension__variable__project=project).count() == 4

    # 6. Verificar estado del proyecto enriquecido y envío del Capítulo 3 a revisión
    estado = obtener_estado_proyecto(owner, project.id)
    assert len(estado["consistency_matrix"]) == 3
    assert len(estado["variables"]) == 2
    assert len(estado["variables"][0]["dimensions"]) == 2

    cap3 = enviar_capitulo_servicio(owner, project.id, 3)
    assert cap3["status"] == Capitulo.Status.READY
