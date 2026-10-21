# Explicación de Código: `backend/thesis/tests/test_descubrimiento_peru.py`

## 1. Propósito y ¿Qué hace?
Prueba el subsistema de antecedentes peruanos: consulta al repositorio ALICIA CONCYTEC, filtro de artículos con filiación en Perú en OpenAlex, normalización léxica del ámbito geográfico (`geografia.py`) y comprobación de la advertencia metodológica obligatoria.

## 2. Justificación Técnica y ¿Por qué lo hace?
Asegura que las búsquedas nacionales capturen adecuadamente variantes ortográficas (con y sin tildes en departamentos como 'Junín', 'Áncash') y que las respuestas contengan la advertencia formal de que los resultados son metadatos y no texto completo verificado.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Simula respuestas HTTP de ALICIA y OpenAlex mediante adaptadores de prueba.
2. Verifica que `inferir_ambito_geografico` reconozca departamentos peruanos y devuelva `REGIONAL_PERU`.
3. Comprueba que la lista consolidada retorne sin duplicados y con metadatos estructurados.

## 4. Componentes y Funciones Clave
* Pruebas de integración HTTP y lógica geográfica determinista.

## 5. Relaciones con Otras Capas y Tablas
* **Servicios:** [`descubrimiento_peru.py`](../../backend/thesis/services/descubrimiento_peru.md) y [`geografia.py`](../../backend/thesis/services/geografia.md).
