"""Catálogo metodológico compartido por el backend y el servidor MCP (Capítulos 1 al 3: P01 a P12)."""

from typing import Any

CATALOGO_PASOS: dict[str, dict[str, Any]] = {
    # Capítulo 1: Selección del Tema y Alcance
    "P01": {
        "capitulo": 1,
        "nombre": "Mapa de temas viables",
        "objetivo": "Generar 10 temas potenciales según intereses y área, con matriz de pros y contras.",
        "entradas_requeridas": ["carrera", "intereses", "area_investigacion"],
    },
    "P02": {
        "capitulo": 1,
        "nombre": "Matriz de factibilidad",
        "objetivo": "Comparar 3 temas preseleccionados evaluando puntajes de 1 al 5 en acceso a datos, relevancia y brecha.",
        "entradas_requeridas": ["temas_candidatos"],
    },
    "P03": {
        "capitulo": 1,
        "nombre": "Alineación ODS y relevancia",
        "objetivo": "Alinear el tema seleccionado con tendencias científicas y los Objetivos de Desarrollo Sostenible (ODS).",
        "entradas_requeridas": ["tema_seleccionado"],
    },
    "P04": {
        "capitulo": 1,
        "nombre": "Delimitación final y título",
        "objetivo": "Formular el título oficial de máximo 20 palabras (Variables + Unidad de análisis + Lugar + Tiempo).",
        "entradas_requeridas": ["tema", "unidad_analisis", "lugar", "periodo"],
    },
    "P05": {
        "capitulo": 1,
        "nombre": "Redacción de la Introducción",
        "objetivo": "Redactar el Capítulo I completo en prosa continua académica.",
        "entradas_requeridas": ["titulo", "delimitacion_confirmada"],
    },
    # Capítulo 2: Problema y Justificación
    "P06": {
        "capitulo": 2,
        "nombre": "Árbol del problema y formulación",
        "objetivo": "Construir causas/efectos y redactar la pregunta general y preguntas específicas.",
        "entradas_requeridas": ["titulo", "unidad_analisis"],
    },
    "P07": {
        "capitulo": 2,
        "nombre": "Justificación de la investigación",
        "objetivo": "Argumentar la relevancia teórica, práctica, metodológica y social del estudio.",
        "entradas_requeridas": ["problema_central"],
    },
    "P08": {
        "capitulo": 2,
        "nombre": "Originalidad y aporte",
        "objetivo": "Explicar la contribución novedosa de la tesis frente a la literatura previa.",
        "entradas_requeridas": ["brecha_detectada", "aporte_propuesto"],
    },
    # Capítulo 3: Objetivos, Preguntas e Hipótesis
    "P09": {
        "capitulo": 3,
        "nombre": "Objetivos de investigación",
        "objetivo": "Formular objetivo general y específicos usando verbos de la Taxonomía de Bloom.",
        "entradas_requeridas": ["problema_central", "preguntas_especificas"],
    },
    "P10": {
        "capitulo": 3,
        "nombre": "Preguntas de investigación alineadas",
        "objetivo": "Verificar correspondencia biunívoca entre preguntas y objetivos con formato ¿?",
        "entradas_requeridas": ["objetivo_general", "objetivos_especificos"],
    },
    "P11": {
        "capitulo": 3,
        "nombre": "Hipótesis y variables",
        "objetivo": "Formular hipótesis general y específicas identificando variable independiente y dependiente.",
        "entradas_requeridas": ["tipo_investigacion", "preguntas", "objetivos"],
    },
    "P12": {
        "capitulo": 3,
        "nombre": "Matriz de operacionalización",
        "objetivo": "Construir matriz de variables, definiciones, dimensiones, indicadores y escala de medición.",
        "entradas_requeridas": ["variables_confirmadas"],
    },
}
