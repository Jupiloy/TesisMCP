# Explicación de Código: `backend/thesis/services/geografia.py`

## 1. Propósito y ¿Qué hace?
Es un servicio de análisis determinista de texto que detecta el **ámbito geográfico** de una investigación o antecedente bibliográfico (Nacional Perú, Regional/Departamental o Internacional).

## 2. Justificación Técnica y ¿Por qué lo hace?
Permite clasificar automáticamente si un antecedente localizado respalda el contexto local (ej. Piura, Lima, Arequipa) o si debe categorizarse como antecedente internacional, apoyando la formulación del título en `P04` y del alcance en `P05`.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Mantiene un diccionario canónico de los 24 departamentos del Perú, la provincia constitucional del Callao y términos clave nacionales.
2. Analiza el título, resumen y contexto espacial mediante expresiones regulares y tokenización.
3. Asigna la clasificación geográfica:
   - Si detecta un departamento peruano -> `REGIONAL_PERU` con el nombre del departamento.
   - Si detecta 'Perú' o instituciones peruanas -> `NACIONAL_PERU`.
   - Si no detecta referencias peruanas -> `INTERNACIONAL`.

## 4. Componentes y Funciones Clave
* `inferir_ambito_geografico(texto: str) -> dict`: Función determinista de análisis léxico.
* `DEPARTAMENTOS_PERU`: Lista de regiones y departamentos normalizados.

## 5. Relaciones con Otras Capas y Tablas
* **Consumidores:** Utilizado por [`descubrimiento_peru.py`](../../backend/thesis/services/descubrimiento_peru.py) y el materializador de consistencia en `P04`.
