"""Caso de ejemplo para ejecutar los 12 pasos metodológicos (Capítulos 1 al 3: P01 a P12) por MCP."""


def _construir_cargas_12_pasos() -> dict[str, tuple[str, dict]]:
    """Retorna (contenido_md, datos_salida) de P01 a P12 basados en la problemática de TesisMCP."""
    titulo_oficial = (
        "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis "
        "en Estudiantes de la UTP Piura, 2026"
    )
    # 18 palabras exactas; contiene:
    # - variables_confirmadas: ["Protocolo MCP", "Formulación Metodológica de Tesis"]
    # - unidad_analisis_confirmada: "Estudiantes"
    # - lugar_confirmado: "UTP Piura"
    # - periodo_confirmado: 2026

    p05_parrafos = [
        (
            "En el contexto global de la educación superior, la elaboración de trabajos de investigación "
            "para la obtención del grado académico enfrenta cuellos de botella estructurales derivados de "
            "la desconexión entre la escritura académica y las reglas metodológicas institucionales. Aunque "
            "los modelos de lenguaje de gran escala han agilizado la redacción preliminar, los estudios "
            "recientes demuestran que la generación libre de texto largo introduce alucinaciones bibliográficas "
            "severas y pérdida de coherencia entre objetivos, variables e indicadores de medición."
        ),
        (
            "A nivel nacional en el Perú, diversas universidades han implementado repositorios digitales y "
            "plataformas web administrativas para el control de trámites de titulación, logrando reducir los "
            "tiempos de registro documental y seguimiento de expedientes. Sin embargo, dichas soluciones se "
            "limitan a la gestión de archivos estáticos en formato PDF o Word sin inspeccionar ni validar "
            "la consistencia interna de la matriz metodológica, dejando toda la carga de verificación "
            "estructural en revisiones manuales asíncronas."
        ),
        (
            "En el ámbito local de la Universidad Tecnológica del Perú (UTP) Sede Piura durante el ciclo 2026, "
            "los estudiantes de Ingeniería de Sistemas e Informática elaboran sus proyectos del Curso Integrador "
            "utilizando procesadores de texto aislados y chats conversacionales sin memoria canónica. Esta "
            "fragmentación provoca que los asesores inviertan gran parte de las sesiones corrigiendo errores "
            "de forma, verbos mal formulados, variables huérfanas y preguntas desalineadas en lugar de profundizar "
            "en el rigor técnico y científico de la solución propuesta."
        ),
        (
            "Frente a esta problemática, resulta imperativo diseñar e implementar una arquitectura híbrida "
            "desacoplada basada en el Model Context Protocol (MCP) que separe la generación asistida por IA "
            "de la validación determinista en servidor (Zero-LLM). De este modo, cada paso metodológico de "
            "los Capítulos 1 al 3 queda resguardado por contratos estrictos, bloqueo optimista y "
            "sincronización relacional de la matriz de consistencia y operacionalización de variables."
        ),
    ]
    p05_md = "\n\n".join(p05_parrafos)
    palabras_p05 = len(p05_md.split())

    return {
        "P01": (
            "# P01: Sondeo y Preselección de Temas\nExploración de 5 candidatos tecnológicos en UTP Sede Piura.",
            {
                "temas_propuestos": [
                    {
                        "id": 1,
                        "titulo_tentativo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis",
                        "pros": ["Acceso directo a cohorte UTP Piura", "Alto impacto en reducción de errores estructurales"],
                        "contras": ["Requiere orquestación estricta entre stdio y PostgreSQL"],
                        "viabilidad_preliminar": "ALTA",
                    },
                    {
                        "id": 2,
                        "titulo_tentativo": "Aplicativo móvil con reconocimiento facial para control de asistencia estudiantil",
                        "pros": ["Hardware disponible en smartphones"],
                        "contras": ["Tema saturado en repositorios locales y restricciones de privacidad biométrica"],
                        "viabilidad_preliminar": "MEDIA",
                    },
                    {
                        "id": 3,
                        "titulo_tentativo": "Sistema predictivo de deserción universitaria mediante redes neuronales profundas",
                        "pros": ["Relevancia institucional"],
                        "contras": ["Datos históricos socioeconómicos restringidos por protección de datos personales"],
                        "viabilidad_preliminar": "BAJA",
                    },
                    {
                        "id": 4,
                        "titulo_tentativo": "Plataforma IoT para monitoreo energético en laboratorios de cómputo",
                        "pros": ["Medición en tiempo real"],
                        "contras": ["Dependencia de adquisición de sensores industriales e instalación eléctrica"],
                        "viabilidad_preliminar": "MEDIA",
                    },
                    {
                        "id": 5,
                        "titulo_tentativo": "Chatbot de consultas administrativas para trámites de matrícula universitaria",
                        "pros": ["Implementación rápida"],
                        "contras": ["Bajo aporte metodológico y alcance meramente informativo"],
                        "viabilidad_preliminar": "MEDIA",
                    },
                ],
                "tema_preseleccionado_id": 1,
            },
        ),
        "P02": (
            "# P02: Matriz de Evaluación Comparativa de Temas\nSelección objetiva del tema ganador (ID 1).",
            {
                "matriz_comparativa": [
                    {
                        "tema_id": 1,
                        "titulo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis",
                        "puntajes": {
                            "acceso_a_datos": 5,
                            "relevancia_profesional": 5,
                            "brecha_conocimiento": 5,
                            "recursos_disponibles": 4,
                        },
                        "puntaje_total": 19,
                        "justificacion_eleccion": "Acceso total a casos de prueba en UTP Sede Piura y brecha clara en arquitecturas MCP con validación Zero-LLM.",
                    },
                    {
                        "tema_id": 2,
                        "titulo": "Aplicativo móvil con reconocimiento facial para control de asistencia estudiantil",
                        "puntajes": {
                            "acceso_a_datos": 3,
                            "relevancia_profesional": 3,
                            "brecha_conocimiento": 2,
                            "recursos_disponibles": 4,
                        },
                        "puntaje_total": 12,
                        "justificacion_eleccion": "Existen múltiples implementaciones previas en la región Piura con baja novedad científica.",
                    },
                    {
                        "tema_id": 4,
                        "titulo": "Plataforma IoT para monitoreo energético en laboratorios de cómputo",
                        "puntajes": {
                            "acceso_a_datos": 3,
                            "relevancia_profesional": 4,
                            "brecha_conocimiento": 3,
                            "recursos_disponibles": 2,
                        },
                        "puntaje_total": 12,
                        "justificacion_eleccion": "Limitaciones presupuestarias y de permisos físicos para intervenir tableros eléctricos.",
                    },
                ],
                "tema_ganador_id": 1,
                "tema_ganador_titulo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis",
            },
        ),
        "P03": (
            "# P03: Alineación con ODS y Líneas de Investigación UTP\nVinculado con el ODS 4 (Educación de Calidad).",
            {
                "ods_principal_numero": 4,
                "ods_principal_nombre": "Educación de Calidad",
                "meta_ods_especifica": "4.4",
                "argumento_alineacion": "Fortalece las competencias investigativas y tecnológicas de los estudiantes universitarios mediante una arquitectura verificable que previene errores metodológicos en trabajos de grado.",
                "linea_utp_vinculada": "Tecnologías Emergentes aplicadas a la Educación Superior y Gestión del Conocimiento",
            },
        ),
        "P04": (
            f"# P04: Delimitación Formal del Título\nTítulo oficial confirmado: **{titulo_oficial}** (18 palabras).",
            {
                "titulo_oficial": titulo_oficial,
                "conteo_palabras": 18,
                "variables_confirmadas": ["Protocolo MCP", "Formulación Metodológica de Tesis"],
                "unidad_analisis_confirmada": "Estudiantes",
                "lugar_confirmado": "UTP Piura",
                "periodo_confirmado": 2026,
            },
        ),
        "P05": (
            p05_md,
            {
                "contenido_markdown": p05_md,
                "num_parrafos": 4,
                "palabras_totales": palabras_p05,
            },
        ),
        "P06": (
            "# P06: Árbol de Problemas y Formulación de Preguntas\nSincronización inicial de la Matriz de Consistencia.",
            {
                "problema_central": "Alta incidencia de inconsistencias estructurales y desalineación metodológica en la formulación de tesis en estudiantes universitarios.",
                "causas_directas": [
                    "Uso de asistentes conversacionales sin validación determinista de esquemas ni estado canónico",
                    "Desconexión entre las matrices de consistencia y operacionalización de variables",
                    "Revisiones docentes manuales sobre documentos estáticos sin trazabilidad de cambios",
                ],
                "efectos_directos": [
                    "Retrasos recurrentes en la aprobación de capítulos y sobrecarga de correcciones repetitivas",
                    "Riesgo de desalineación entre preguntas, objetivos, hipótesis y dimensiones",
                    "Frustración estudiantil y dilatación en el proceso de titulación profesional",
                ],
                "pregunta_general": "¿De qué manera el Protocolo MCP optimiza la Formulación Metodológica de Tesis en estudiantes de la UTP Piura, 2026?",
                "preguntas_especificas": [
                    "¿Cómo influye la validación determinista de contratos en la coherencia estructural de la matriz de consistencia?",
                    "¿En qué medida la exploración estructurada de literatura mejora la delimitación del problema de investigación?",
                    "¿Cómo impacta el flujo de revisión con anclajes inmutables en la resolución de observaciones del asesor?",
                ],
            },
        ),
        "P07": (
            "# P07: Justificación en Cuatro Dimensiones\nSustento teórico, práctico, metodológico y social.",
            {
                "justificaciones": [
                    {
                        "dimension": "TEORICA",
                        "argumento": "Aporta un modelo arquitectónico que integra el protocolo abierto MCP con invariantes de dominio relacionales para acotar asistentes de IA en tareas de formulación académica.",
                    },
                    {
                        "dimension": "PRACTICA",
                        "argumento": "Proporciona a los tesistas y asesores de la UTP Sede Piura una plataforma centralizada que automatiza la verificación estructural de los pasos metodológicos y agiliza la retroalimentación docente.",
                    },
                    {
                        "dimension": "METODOLOGICA",
                        "argumento": "Demuestra que la separación estricta entre la generación asistida por lenguaje natural y los validadores deterministas Zero-LLM garantiza la trazabilidad entre preguntas, objetivos, hipótesis, variables e indicadores.",
                    },
                    {
                        "dimension": "SOCIAL",
                        "argumento": "Democratiza el acompañamiento metodológico riguroso en estudiantes de ingeniería de la región Piura, reduciendo las brechas formativas y elevando la calidad de los proyectos universitarios.",
                    },
                ],
                "resumen_ejecutivo": "El proyecto TesisMCP se justifica integralmente al resolver la tensión entre la asistencia generativa de IA y el rigor metodológico universitario mediante contratos verificables, matriz de consistencia relacional y supervisión docente auditable.",
            },
        ),
        "P08": (
            "# P08: Brecha de Investigación y Aporte Propuesto\nDefinición del vacío tecnológico y estado de evidencia.",
            {
                "brecha_detectada": "Los sistemas web universitarios locales solo gestionan trámites administrativos, mientras que los asistentes conversacionales carecen de persistencia relacional canónica para validar matrices de consistencia.",
                "aporte_propuesto": "Una plataforma web con arquitectura desacoplada y servidor MCP que valida determinísticamente los capítulos iniciales de formulación metodológica en PostgreSQL.",
                "estado_evidencia": "EVIDENCIA_PENDIENTE",
            },
        ),
        "P09": (
            "# P09: Formulación de Objetivos (Taxonomía de Bloom)\nAlineación 1 a 1 con las preguntas de investigación.",
            {
                "objetivo_general": "Determinar de qué manera el Protocolo MCP optimiza la Formulación Metodológica de Tesis en estudiantes de la UTP Piura, 2026",
                "objetivos_especificos": [
                    "Analizar la influencia de la validación determinista de contratos en la coherencia estructural de la matriz de consistencia",
                    "Evaluar el efecto de la exploración estructurada de literatura sobre la delimitación del problema de investigación",
                    "Demostrar el impacto del flujo de revisión con anclajes inmutables en la resolución de observaciones del asesor",
                ],
            },
        ),
        "P10": (
            "# P10: Consolidación de Preguntas de Investigación\nSincronización canónica en FilaConsistencia.",
            {
                "pregunta_general": "¿De qué manera el Protocolo MCP optimiza la Formulación Metodológica de Tesis en estudiantes de la UTP Piura, 2026?",
                "preguntas_especificas": [
                    "¿Cómo influye la validación determinista de contratos en la coherencia estructural de la matriz de consistencia?",
                    "¿En qué medida la exploración estructurada de literatura mejora la delimitación del problema de investigación?",
                    "¿Cómo impacta el flujo de revisión con anclajes inmutables en la resolución de observaciones del asesor?",
                ],
            },
        ),
        "P11": (
            "# P11: Formulación de Hipótesis y Variables Relacionales\nMaterialización en VariableInvestigacion y VariableFilaConsistencia.",
            {
                "tipo_investigacion": "EXPLICATIVA",
                "hipotesis_general": "La arquitectura basada en el Protocolo MCP optimiza significativamente la Formulación Metodológica de Tesis en estudiantes de la UTP Piura, 2026.",
                "hipotesis_especificas": [
                    "La validación determinista de contratos incrementa significativamente la coherencia estructural de la matriz de consistencia.",
                    "La exploración estructurada de literatura mejora significativamente la delimitación del problema de investigación.",
                    "El flujo de revisión con anclajes inmutables mejora significativamente la tasa de resolución de observaciones del asesor.",
                ],
                "variable_independiente": "Protocolo MCP",
                "variable_dependiente": "Formulación Metodológica de Tesis",
            },
        ),
        "P12": (
            "# P12: Matriz de Operacionalización de Variables\nMaterialización de Dimensiones (DimensionVariable) e Indicadores (Indicador).",
            {
                "matriz_operacionalizacion": [
                    {
                        "variable": "Protocolo MCP",
                        "definicion_conceptual": "Estándar de comunicación desacoplada que conecta agentes de lenguaje con herramientas y validadores deterministas del dominio académico.",
                        "definicion_operacional": "Evaluación técnica de la validación de contratos Pydantic, exploración bibliográfica y control de concurrencia optimista.",
                        "dimensiones": ["Validación Determinista", "Exploración Bibliográfica"],
                        "indicadores": ["Cumplimiento de contratos por paso", "Cobertura de búsqueda en catálogos"],
                        "escala_medicion": "ORDINAL",
                    },
                    {
                        "variable": "Formulación Metodológica de Tesis",
                        "definicion_conceptual": "Proceso sistemático de estructuración coherente de problemas, objetivos, hipótesis y variables de investigación universitaria.",
                        "definicion_operacional": "Medición de la consistencia cruzada entre capítulos y la eficiencia en el levantamiento de observaciones del asesor docente.",
                        "dimensiones": ["Coherencia Estructural", "Eficiencia de Revisión Docente"],
                        "indicadores": ["Índice de trazabilidad de la matriz", "Resolución efectiva de observaciones"],
                        "escala_medicion": "ORDINAL",
                    },
                ]
            },
        ),
    }
