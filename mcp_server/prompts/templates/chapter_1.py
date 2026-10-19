"""Plantillas de prompts para el Capítulo 1: Selección del Tema y Alcance (P01 a P05)."""

_P05_EXAMPLE = "\n\n".join([
    "En el contexto internacional, los estudiantes que redactan una tesis necesitan organizar preguntas, objetivos y fuentes de manera coherente. Un asistente de escritura puede proponer borradores, pero cada dato bibliográfico y cada afirmación empírica requieren una comprobación independiente. Este párrafo muestra cómo delimitar el problema sin atribuir a investigaciones ajenas resultados que todavía no se han revisado. Antes de usarlo en un proyecto real, el tesista debe reemplazar estas frases generales por evidencia localizada y citada.",
    "En el contexto nacional, la revisión de antecedentes debe partir de documentos identificables y de sus textos completos cuando se describan métodos o resultados. Las fichas de catálogos sirven para descubrir candidatos, no para concluir qué ocurrió dentro de un estudio. El redactor deberá registrar los títulos y autorías de las portadas, distinguir a los autores de los asesores y señalar las páginas físicas que respaldan las afirmaciones que finalmente incluya en esta sección.",
    "En el contexto local, conviene definir el lugar, la población y el periodo de la investigación antes de describir necesidades concretas. La existencia de dificultades, sus causas y su frecuencia deberán documentarse mediante observaciones o datos recogidos con instrumentos explícitos. Hasta contar con esos datos, la introducción debe presentar la situación como un problema por estudiar y evitar porcentajes, comparaciones de rendimiento o afirmaciones sobre estudiantes y docentes que no tengan una fuente verificable.",
    "La propuesta técnica consiste en guiar la formulación metodológica mediante pasos estructurados y conservar las versiones que revisa el asesor. Los controles automáticos pueden verificar formatos, relaciones entre campos y coincidencias literales con extractos, pero no sustituyen la lectura crítica de las fuentes ni la evaluación científica de una tesis. La intervención, sus indicadores y el procedimiento de evaluación se describirán con precisión en las secciones siguientes. Cualquier mejora atribuida al sistema deberá calcularse a partir de datos originales del estudio.",
])

CHAPTER_1_TEMPLATES = {
    "P01": {
        "step_code": "P01",
        "prompt_name": "paso_p01_mapa_temas",
        "titulo": "P01: Mapa de Temas Viables",
        "descripcion": "Genera 5 a 10 temas potenciales según intereses y área, con pros, contras y viabilidad.",
        "guia_metodologica": """
En la elección del tema de tesis para ingeniería:
1. Genera entre 5 y 10 temas potenciales vinculados al área de especialidad.
2. Cada tema debe tener un título tentativo claro, lista de pros y contras fundamentados, y viabilidad preliminar (ALTA, MEDIA o BAJA).
3. Preselecciona el tema más prometedor según el acceso real a la población/datos y la relevancia tecnológica.
""",
        "esquema_json_ejemplo": {
            "temas_propuestos": [
                {
                    "id": 1,
                    "titulo_tentativo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis",
                    "pros": ["Acceso directo a cohorte de estudiantes", "Alto impacto contra alucinaciones de IA"],
                    "contras": ["Requiere arquitectura cliente-servidor rigurosa"],
                    "viabilidad_preliminar": "ALTA"
                },
                {
                    "id": 2,
                    "titulo_tentativo": "Aplicación móvil para la gestión de incidencias en redes de telecomunicaciones",
                    "pros": ["Infraestructura móvil estándar"],
                    "contras": ["Acceso restringido a datos de operadoras"],
                    "viabilidad_preliminar": "MEDIA"
                },
                {
                    "id": 3,
                    "titulo_tentativo": "Modelo predictivo de rendimiento académico con algoritmos de aprendizaje supervisado",
                    "pros": ["Algoritmos bien documentados"],
                    "contras": ["Trámites de privacidad de datos estudiantiles"],
                    "viabilidad_preliminar": "BAJA"
                },
                {
                    "id": 4,
                    "titulo_tentativo": "Plataforma IoT para monitoreo de consumo eléctrico en laboratorios universitarios",
                    "pros": ["Medición en tiempo real"],
                    "contras": ["Costos de sensores industriales"],
                    "viabilidad_preliminar": "MEDIA"
                },
                {
                    "id": 5,
                    "titulo_tentativo": "Asistente conversacional para consultas administrativas en ventanilla de matrícula",
                    "pros": ["Despliegue rápido"],
                    "contras": ["Bajo aporte metodológico y alcance meramente informativo"],
                    "viabilidad_preliminar": "MEDIA"
                }
            ],
            "tema_preseleccionado_id": 1
        }
    },
    "P02": {
        "step_code": "P02",
        "prompt_name": "paso_p02_matriz_factibilidad",
        "titulo": "P02: Matriz de Factibilidad Comparativa",
        "descripcion": "Compara exactamente 3 temas finalistas con puntajes del 1 al 5 en 4 criterios objetivos.",
        "guia_metodologica": """
Para seleccionar con rigor empírico el tema definitivo:
1. Evalúa exactamente 3 temas preseleccionados.
2. Asigna puntajes del 1 al 5 en 4 dimensiones:
   - Acceso a datos (¿puedes medir o recolectar información en campo?).
   - Relevancia profesional (¿aporta al perfil de egreso en ingeniería?).
   - Brecha de conocimiento (¿resuelve un vacío existente en la literatura?).
   - Recursos disponibles (¿tiempo, hardware y permisos viables?).
3. La suma debe coincidir exactamente con el puntaje_total (entre 4 y 20 puntos).
4. Declara el tema ganador con su justificación detallada (mínimo 20 caracteres).
""",
        "esquema_json_ejemplo": {
            "matriz_comparativa": [
                {
                    "tema_id": 1,
                    "titulo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis",
                    "puntajes": {
                        "acceso_a_datos": 5,
                        "relevancia_profesional": 5,
                        "brecha_conocimiento": 5,
                        "recursos_disponibles": 4
                    },
                    "puntaje_total": 19,
                    "justificacion_eleccion": "Acceso total a casos de prueba en la universidad y brecha clara en arquitecturas MCP con validación Zero-LLM."
                },
                {
                    "tema_id": 2,
                    "titulo": "Aplicación móvil para la gestión de incidencias en redes de telecomunicaciones",
                    "puntajes": {
                        "acceso_a_datos": 3,
                        "relevancia_profesional": 4,
                        "brecha_conocimiento": 3,
                        "recursos_disponibles": 3
                    },
                    "puntaje_total": 13,
                    "justificacion_eleccion": "Tema relevante pero con incertidumbre en permisos de empresas de telecomunicaciones."
                },
                {
                    "tema_id": 4,
                    "titulo": "Plataforma IoT para monitoreo de consumo eléctrico en laboratorios universitarios",
                    "puntajes": {
                        "acceso_a_datos": 3,
                        "relevancia_profesional": 3,
                        "brecha_conocimiento": 3,
                        "recursos_disponibles": 2
                    },
                    "puntaje_total": 11,
                    "justificacion_eleccion": "Riesgo presupuestario por costo de sensores de corriente no contemplados."
                }
            ],
            "tema_ganador_id": 1,
            "tema_ganador_titulo": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis"
        }
    },
    "P03": {
        "step_code": "P03",
        "prompt_name": "paso_p03_alineacion_ods",
        "titulo": "P03: Alineación con ODS y Tendencias 2026",
        "descripcion": "Vincula el tema seleccionado con un Objetivo de Desarrollo Sostenible (ODS) y su meta específica.",
        "guia_metodologica": """
Alinea el tema de tesis con la agenda 2030 de las Naciones Unidas:
1. Identifica el ODS correspondiente (ej. ODS-04 Educación de Calidad, ODS-09 Industria e Innovación).
2. Especifica el código de meta formal (ej. 'ODS-04:4.4' o 'ODS-09:9.5').
3. Argumenta la justificación del ODS con al menos 20 caracteres y fundamenta las tendencias tecnológicas vigentes al 2026.
""",
        "esquema_json_ejemplo": {
            "ods_principal_numero": 4,
            "ods_principal_nombre": "Educación de Calidad",
            "meta_ods_especifica": "4.4",
            "argumento_alineacion": "El ejemplo vincula la formación en investigación con competencias técnicas; el tesista debe cotejar la pertinencia de esta meta con el alcance real de su proyecto.",
            "linea_utp_vinculada": "Línea institucional por confirmar con la documentación de la carrera"
        }
    },
    "P04": {
        "step_code": "P04",
        "prompt_name": "paso_p04_delimitacion_titulo",
        "titulo": "P04: Delimitación Final y Formulación del Título",
        "descripcion": "Formula el título oficial de máximo 20 palabras: Variables + Unidad de Análisis + Lugar + Periodo.",
        "guia_metodologica": """
Regla de oro del título universitario:
1. Longitud máxima estricta: 20 palabras (el backend rechazará cualquier título de 21 o más palabras).
2. Estructura canónica obligatoria:
   [Variable Independiente / Propuesta] + [Variable Dependiente / Problema] + en [Unidad de análisis] + de [Lugar], [Periodo].
3. Todas las variables y delimitaciones deben estar confirmadas explícitamente.
""",
        "esquema_json_ejemplo": {
            "variables_confirmadas": [
                "Protocolo MCP",
                "Formulación Metodológica de Tesis"
            ],
            "unidad_analisis_confirmada": "Estudiantes",
            "lugar_confirmado": "UTP Piura",
            "periodo_confirmado": 2026,
            "titulo_oficial": "Sistema Web con Protocolo MCP para la Formulación Metodológica de Tesis en Estudiantes de la UTP Piura, 2026",
            "conteo_palabras": 18
        }
    },
    "P05": {
        "step_code": "P05",
        "prompt_name": "paso_p05_redaccion_introduccion",
        "titulo": "P05: Redacción de la Introducción (Capítulo I)",
        "descripcion": "Redacta el Capítulo I completo en prosa continua académica estructurado en 4 niveles.",
        "guia_metodologica": """
Estructura académica de la Introducción (Capítulo I):
1. Contexto global: panorama internacional del problema y limitaciones de los enfoques convencionales.
2. Contexto nacional: situación en el Perú, avances en repositorios y vacíos estructurales.
3. Contexto local: diagnóstico empírico en la sede y población de estudio (ej. UTP Piura).
4. Solución propuesta: presentación técnica de la solución tecnológica y su impacto esperado.
5. `contenido_markdown` debe tener al menos 250 palabras y tres párrafos; `num_parrafos` y `palabras_totales` deben coincidir con el texto.
""",
        "esquema_json_ejemplo": {
            "contenido_markdown": _P05_EXAMPLE,
            "num_parrafos": len(_P05_EXAMPLE.split("\n\n")),
            "palabras_totales": len(_P05_EXAMPLE.split()),
        }
    }
}
