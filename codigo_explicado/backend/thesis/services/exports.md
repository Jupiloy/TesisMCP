# Explicación de Código: `backend/thesis/services/exports.py`

## 1. Propósito y ¿Qué hace?
Genera y consolida el **borrador completo en formato Markdown** de los Capítulos 1, 2 y 3 del proyecto de tesis. Ensambla el título oficial, la delimitación temática, la realidad problemática, las justificaciones, la Matriz de Consistencia y la Matriz de Operacionalización en un documento académico coherente y estructurado.

## 2. Justificación Técnica y ¿Por qué lo hace?
Permite a tesistas y asesores exportar el documento unificado para su lectura, conversión a PDF/DOCX institucional o presentación de avance, sin depender de un cliente específico.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Consulta el `PerfilInvestigacion` y sus `ProgresoPaso` asociados al proyecto.
2. Recupera las revisiones vigentes de los Capítulos 1, 2 y 3 desde `RevisionCapitulo`.
3. Concatena los bloques con encabezados de nivel Markdown (`# Capítulo 1`, `## 1.1 Planteamiento`, etc.).
4. Si las matrices relacionales están materializadas, consulta `FilaConsistencia` y genera una tabla en formato Markdown con las columnas: Problema, Objetivo, Hipótesis, Variables e Indicadores.

## 4. Componentes y Funciones Clave
* `exportar_borrador_markdown_servicio(project_id, user) -> str`: Genera el documento consolidado.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos:** Lee `PerfilInvestigacion`, `RevisionCapitulo`, `FilaConsistencia`, `VariableInvestigacion`, `DimensionVariable` e `Indicador`.
* **Pruebas:** Verificado en [`backend/thesis/tests/test_extended_steps.py`](../../backend/thesis/tests/test_extended_steps.py).
