"""Plantillas de prompts para el Capítulo 3: Objetivos, Preguntas e Hipótesis (P09 a P12)."""

PLANTILLAS_CAPITULO_3 = {
    "P09": {
        "codigo_paso": "P09",
        "nombre_prompt": "paso_p09_objetivos_smart",
        "titulo": "P09: Objetivos de Investigación (Taxonomía de Bloom)",
        "descripcion": "Formula el objetivo general y específicos usando verbos en infinitivo de la Taxonomía de Bloom.",
        "guia_metodologica": """
Reglas estrictas para los objetivos de investigación:
1. El objetivo general y cada uno de los objetivos específicos (entre 2 y 4) DEBEN iniciar con un verbo de Bloom válido en infinitivo:
   Verbos permitidos: DETERMINAR, ANALIZAR, EVALUAR, DISEÑAR, IMPLEMENTAR, PROPONER, IDENTIFICAR, COMPARAR, ESTABLECER, EXAMINAR, MEDIR, DEMOSTRAR, OPTIMIZAR, DESARROLLAR, MODELAR.
2. Cada objetivo debe ser SMART (Específico, Medible, Alcanzable, Relevante y Temporal).
3. Debe existir correspondencia biunívoca con las preguntas de investigación formuladas.
""",
        "esquema_json_ejemplo": {
            "objetivo_general": "Determinar la influencia de un sistema web con protocolo MCP en la formulación metodológica de tesis en estudiantes de la UTP Piura, 2026.",
            "objetivos_especificos": [
                "Diseñar una arquitectura desacoplada para la validación determinista de la matriz metodológica de tesis.",
                "Implementar un servidor MCP que certifique la trazabilidad física de antecedentes sin alucinaciones.",
                "Evaluar el impacto del circuito determinista en la reducción de observaciones docentes en revisiones de tesis."
            ]
        }
    },
    "P10": {
        "codigo_paso": "P10",
        "nombre_prompt": "paso_p10_preguntas_alineadas",
        "titulo": "P10: Preguntas de Investigación Alineadas",
        "descripcion": "Verifica y consolida las preguntas general y específicas con signos de interrogación ¿?",
        "guia_metodologica": """
Alineación metodológica de preguntas:
1. Todas las preguntas (general y entre 2 y 4 específicas) deben iniciar obligatoriamente con '¿' y terminar con '?'.
2. La pregunta general debe corresponder de manera idéntica al objetivo general (salvo por el pronombre interrogativo vs. el verbo de Bloom).
3. Cada pregunta específica debe reflejar su respectivo objetivo específico.
""",
        "esquema_json_ejemplo": {
            "pregunta_general": "¿De qué manera un sistema web con protocolo MCP influye en la formulación metodológica de tesis en estudiantes de la UTP Piura, 2026?",
            "preguntas_especificas": [
                "¿Cómo influye el diseño de una arquitectura desacoplada en la consistencia de la matriz metodológica de tesis?",
                "¿En qué medida la implementación de un servidor MCP reduce las alucinaciones bibliográficas en los antecedentes?",
                "¿Cómo impacta la evaluación del circuito determinista en el tiempo de subsanación de observaciones docentes?"
            ]
        }
    },
    "P11": {
        "codigo_paso": "P11",
        "nombre_prompt": "paso_p11_hipotesis_variables",
        "titulo": "P11: Hipótesis de Investigación y Variables",
        "descripcion": "Formula la hipótesis general, específicas e identifica la variable independiente y dependiente.",
        "guia_metodologica": """
Formulación de hipótesis y asignación de variables:
1. Tipo de investigación: debe ser uno de: APLICADA, BASICA, DESCRIPTIVA, CORRELACIONAL o EXPLICATIVA.
2. Hipótesis general y entre 2 y 4 específicas que respondan directamente a las preguntas de investigación.
3. Variable independiente: la causa o propuesta tecnológica (ej. 'Protocolo MCP' o 'Sistema Web con Protocolo MCP').
4. Variable dependiente: el efecto o problemática a mejorar (ej. 'Formulación Metodológica de Tesis').
""",
        "esquema_json_ejemplo": {
            "tipo_investigacion": "APLICADA",
            "hipotesis_general": "La implementación de un sistema web con protocolo MCP mejora significativamente la formulación metodológica de tesis en estudiantes de la UTP Piura, 2026.",
            "hipotesis_especificas": [
                "El diseño de la arquitectura desacoplada incrementa la consistencia interna de la matriz de investigación.",
                "La intermediación del servidor MCP elimina las alucinaciones bibliográficas en los antecedentes de tesis.",
                "El circuito determinista de revisión reduce el número de observaciones emitidas por los asesores docentes."
            ],
            "variable_independiente": "Sistema Web con Protocolo MCP",
            "variable_dependiente": "Formulación Metodológica de Tesis"
        }
    },
    "P12": {
        "codigo_paso": "P12",
        "nombre_prompt": "paso_p12_operacionalizacion",
        "titulo": "P12: Matriz de Operacionalización de Variables",
        "descripcion": "Descompone cada variable en definición conceptual, operacional, dimensiones, indicadores y escala.",
        "guia_metodologica": """
Estructura rigurosa de la matriz de operacionalización:
1. Define cada variable con:
   - Definición conceptual (fundamentación teórica formal, 20 a 400 caracteres).
   - Definición operacional (cómo se medirá o implementará en la práctica, 20 a 400 caracteres).
   - Dimensiones: entre 1 y 6 dimensiones analíticas.
   - Indicadores: entre 1 y 10 indicadores concretos y medibles.
   - Escala de medición: debe ser NOMINAL, ORDINAL, INTERVALO o RAZON.
2. Debe haber coherencia directa entre los indicadores y los ítems que se formularán en el Capítulo 7.
""",
        "esquema_json_ejemplo": {
            "matriz_operacionalizacion": [
                {
                    "variable": "Sistema Web con Protocolo MCP",
                    "definicion_conceptual": "Arquitectura de software cliente-servidor basada en el estándar abierto Model Context Protocol que desacopla la asistencia generativa de la persistencia determinista.",
                    "definicion_operacional": "Implementación técnica mediante servidor stdio con herramientas tipadas, puente criptográfico de autenticación y validadores Pydantic en backend Django.",
                    "dimensiones": ["Arquitectura del Protocolo MCP", "Determinismo y Seguridad Zero-LLM"],
                    "indicadores": ["Tiempo de respuesta de herramientas MCP en milisegundos", "Tasa de bloqueo de esquemas inválidos"],
                    "escala_medicion": "RAZON"
                },
                {
                    "variable": "Formulación Metodológica de Tesis",
                    "definicion_conceptual": "Proceso académico estructurado mediante el cual el estudiante articula el problema, objetivos, variables e instrumentos de su proyecto de grado.",
                    "definicion_operacional": "Medición empírica del cumplimiento de invariantes científicas y de la fidelidad textual en citas de antecedentes sin alucinaciones.",
                    "dimensiones": ["Consistencia Metodológica", "Fidelidad Documental Grounded"],
                    "indicadores": ["Índice de coherencia biunívoca en matriz", "Porcentaje de citas respaldadas en texto completo de PDFs"],
                    "escala_medicion": "INTERVALO"
                }
            ]
        }
    }
}
