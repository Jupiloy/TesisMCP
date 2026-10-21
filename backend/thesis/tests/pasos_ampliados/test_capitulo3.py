from uuid import uuid4

import pytest

from thesis.models import Capitulo, FilaConsistencia, VariableFilaConsistencia, Indicador, VariableInvestigacion, DimensionVariable
from thesis.services.errores import ErrorDominio
from thesis.services.proyectos import obtener_estado_proyecto
from thesis.services.pasos import guardar_paso_servicio, enviar_capitulo_servicio


def test_flujo_completo_capitulo_3_persistencia_relacional_y_consistencia(proyecto_base_con_p08):
    tesista, proyecto = proyecto_base_con_p08

    # 1. Fallo si P09 tiene distinto número de objetivos específicos que preguntas específicas en P06 (2)
    with pytest.raises(ErrorDominio) as error_desajuste:
        guardar_paso_servicio(
            usuario=tesista,
            id_proyecto=proyecto.id,
            codigo_paso="P09",
            contenido_md="# Objetivos con desajuste",
            datos_salida={
                "objetivo_general": "Determinar la influencia del protocolo MCP en la reducción de observaciones",
                "objetivos_especificos": [
                    "Analizar la tasa de comentarios resueltos en cada entrega",
                    "Evaluar el tiempo promedio de respuesta del asesor docente",
                    "Comparar la satisfacción estudiantil entre ciclos",
                ],
            },
            version_esperada=0,
            clave_idempotencia=str(uuid4()),
        )
    assert error_desajuste.value.codigo == "INCONSISTENCIA_METODOLOGICA"

    # 2. Guardado exitoso de P09
    resultado_p09 = guardar_paso_servicio(
        usuario=tesista,
        id_proyecto=proyecto.id,
        codigo_paso="P09",
        contenido_md="# Capítulo 3: Objetivos\n\nEl objetivo general es determinar la influencia...",
        datos_salida={
            "objetivo_general": "Determinar la influencia del protocolo MCP en la reducción de observaciones",
            "objetivos_especificos": [
                "Analizar la tasa de comentarios resueltos en cada entrega",
                "Evaluar el tiempo promedio de respuesta del asesor docente",
            ],
        },
        version_esperada=0,
        clave_idempotencia=str(uuid4()),
    )
    assert resultado_p09["numero_capitulo"] == 3
    assert resultado_p09["version_estado"] == 1
    assert FilaConsistencia.objects.get(project=proyecto, ordinal=0).objective_text.startswith("Determinar")

    # 3. Guardado exitoso de P10
    resultado_p10 = guardar_paso_servicio(
        usuario=tesista,
        id_proyecto=proyecto.id,
        codigo_paso="P10",
        contenido_md="# Preguntas Consolidadas",
        datos_salida={
            "pregunta_general": "¿De qué manera influye el protocolo MCP en la reducción de observaciones?",
            "preguntas_especificas": [
                "¿Cuál es la tasa de comentarios resueltos en cada entrega?",
                "¿Cuál es el tiempo promedio de respuesta del asesor docente?",
            ],
        },
        version_esperada=1,
        clave_idempotencia=str(uuid4()),
    )
    assert resultado_p10["version_estado"] == 2

    # 4. Guardado exitoso de P11 (Hipótesis y Variables relacionales)
    resultado_p11 = guardar_paso_servicio(
        usuario=tesista,
        id_proyecto=proyecto.id,
        codigo_paso="P11",
        contenido_md="# Hipótesis y Variables",
        datos_salida={
            "tipo_investigacion": "APLICADA",
            "hipotesis_general": "El protocolo MCP influye significativamente en la reducción de observaciones",
            "hipotesis_especificas": [
                "La tasa de comentarios resueltos incrementa con la validación por contratos",
                "El tiempo promedio de respuesta del asesor disminuye mediante anclajes de texto",
            ],
            "variable_independiente": "protocolo MCP",
            "variable_dependiente": "reducción de observaciones",
        },
        version_esperada=2,
        clave_idempotencia=str(uuid4()),
    )
    assert resultado_p11["version_estado"] == 3
    assert VariableInvestigacion.objects.filter(project=proyecto).count() == 2
    assert VariableFilaConsistencia.objects.filter(consistency_row__project=proyecto).count() == 6  # 3 filas x 2 variables

    # 5. Guardado exitoso de P12 (Matriz de Operacionalización -> Dimensiones e Indicadores)
    resultado_p12 = guardar_paso_servicio(
        usuario=tesista,
        id_proyecto=proyecto.id,
        codigo_paso="P12",
        contenido_md="# Matriz de Operacionalización de Variables",
        datos_salida={
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
        version_esperada=3,
        clave_idempotencia=str(uuid4()),
    )
    assert resultado_p12["version_estado"] == 4
    assert DimensionVariable.objects.filter(variable__project=proyecto).count() == 4
    assert Indicador.objects.filter(dimension__variable__project=proyecto).count() == 4

    # 6. Verificar estado del proyecto enriquecido y envío del Capítulo 3 a revisión
    estado = obtener_estado_proyecto(tesista, proyecto.id)
    assert len(estado["matriz_consistencia"]) == 3
    assert len(estado["variables"]) == 2
    assert len(estado["variables"][0]["dimensiones"]) == 2

    capitulo_3 = enviar_capitulo_servicio(tesista, proyecto.id, 3)
    assert capitulo_3["estado"] == Capitulo.Status.EN_REVISION
