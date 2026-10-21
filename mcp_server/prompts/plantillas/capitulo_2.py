"""Plantillas de prompts para el Capítulo 2: Problema y Justificación (P06 a P08)."""

PLANTILLAS_CAPITULO_2 = {
    "P06": {
        "codigo_paso": "P06",
        "nombre_prompt": "paso_p06_arbol_problema",
        "titulo": "P06: Árbol del Problema y Preguntas de Investigación",
        "descripcion": "Construye el problema central, causas, efectos y formula la pregunta general y específicas con signos ¿?",
        "guia_metodologica": """
En la formulación del problema de investigación:
1. Problema central: describe con claridad el cuello de botella tecnológico o empírico (15 a 250 caracteres).
2. Causas directas: identifica entre 2 y 5 raíces causales.
3. Efectos directos: identifica entre 2 y 5 impactos negativos observables.
4. Pregunta general: debe iniciar obligatoriamente con '¿' y terminar con '?' (20 a 250 caracteres), relacionando las variables en el contexto del estudio.
5. Preguntas específicas: entre 2 y 4 interrogantes con signos '¿' y '?' que descomponen el problema por dimensiones o fases.
""",
        "esquema_json_ejemplo": {
            "problema_central": "Dispersión metodológica y alta tasa de alucinación bibliográfica en borradores de tesis",
            "causas_directas": [
                "Uso de modelos de lenguaje sin restricciones deterministas de validación",
                "Falta de trazabilidad física entre las citas redactadas y los PDFs primarios",
                "Revisiones docentes manuales asíncronas sobrecargadas por errores de forma"
            ],
            "efectos_directos": [
                "Rechazo reiterado de planes de tesis por inconsistencia en variables",
                "Pérdida de tiempo lectivo en subsanación de observaciones de formato",
                "Riesgo de fraude académico involuntario por citas sintéticas inexistentes"
            ],
            "pregunta_general": "¿De qué manera un sistema web con protocolo MCP influye en la formulación metodológica de tesis en estudiantes de la UTP Piura, 2026?",
            "preguntas_especificas": [
                "¿Cómo influye la arquitectura desacoplada en la consistencia de la matriz metodológica de tesis?",
                "¿En qué medida el protocolo MCP reduce las alucinaciones bibliográficas en la formulación de antecedentes?",
                "¿Cómo impacta el circuito determinista en el tiempo de revisión docente de los capítulos de tesis?"
            ]
        }
    },
    "P07": {
        "codigo_paso": "P07",
        "nombre_prompt": "paso_p07_justificacion",
        "titulo": "P07: Justificación de la Investigación (4 Dimensiones)",
        "descripcion": "Argumenta la justificación en las cuatro dimensiones requeridas: Teórica, Práctica, Metodológica y Social.",
        "guia_metodologica": """
Para la justificación de una tesis de ingeniería se exigen exactamente cuatro dimensiones:
1. TEORICA: Aporte a la literatura sobre arquitecturas de software, protocolos de IA o métodos científicos (mínimo 60 caracteres).
2. PRACTICA: Solución tangible a un problema real de estudiantes y docentes en la universidad (mínimo 60 caracteres).
3. METODOLOGICA: Nuevos procedimientos, validadores deterministas o trazabilidad de instrumentos (mínimo 60 caracteres).
4. SOCIAL: Impacto en la graduación oportuna, democratización de herramientas de calidad y ética académica (mínimo 60 caracteres).
5. Resumen ejecutivo consolidado de al menos 80 caracteres.
""",
        "esquema_json_ejemplo": {
            "justificaciones": [
                {
                    "dimension": "TEORICA",
                    "argumento": "Aporta evidencia sobre la efectividad de separar la inferencia generativa probabilística de la validación formal en bases de datos relacionales."
                },
                {
                    "dimension": "PRACTICA",
                    "argumento": "Resuelve la sobrecarga operativa de asesores universitarios mediante un panel con observaciones ancladas y bloqueo de aprobación por guardas."
                },
                {
                    "dimension": "METODOLOGICA",
                    "argumento": "Introduce una secuencia verificable de treinta y dos contratos Pydantic que garantizan consistencia biunívoca entre problemas, objetivos e instrumentos."
                },
                {
                    "dimension": "SOCIAL",
                    "argumento": "Promueve la titulación universitaria oportuna y la integridad académica reduciendo el abandono de tesis por frustración metodológica."
                }
            ],
            "resumen_ejecutivo": "La investigación se justifica integralmente al articular rigor teórico en protocolos abiertos de inteligencia artificial con soluciones prácticas y éticas para la educación superior."
        }
    },
    "P08": {
        "codigo_paso": "P08",
        "nombre_prompt": "paso_p08_originalidad_aporte",
        "titulo": "P08: Originalidad y Aporte del Estudio",
        "descripcion": "Define con precisión la brecha detectada en la literatura y el aporte innovador propuesto.",
        "guia_metodologica": """
Define la novedad científica de la tesis:
1. Brecha detectada: identifica qué no han resuelto los sistemas de gestión de tesis tradicionales ni las IAs comerciales (30 a 400 caracteres).
2. Aporte propuesto: explica cómo tu solución cubre esa brecha de forma única (30 a 400 caracteres).
3. Estado de evidencia: se establece en 'EVIDENCIA_PENDIENTE' hasta corroborarse en la revisión de literatura del Capítulo 4.
""",
        "esquema_json_ejemplo": {
            "brecha_detectada": "Los repositorios universitarios existentes solo almacenan documentos finales estáticos y los asistentes de IA comerciales carecen de validación determinista de reglas metodológicas.",
            "aporte_propuesto": "Desarrollo de un servidor MCP con arquitectura Zero-LLM que audita la consistencia interna y la procedencia física de citas en tiempo real antes de persistir.",
            "estado_evidencia": "EVIDENCIA_PENDIENTE"
        }
    }
}
