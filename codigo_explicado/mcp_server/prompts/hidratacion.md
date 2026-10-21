# Explicación de Código: `mcp_server/prompts/hidratacion.py`

## 1. Propósito y ¿Qué hace?
Es el **motor de hidratación de contexto** para los prompts del servidor MCP. A partir del UUID de un proyecto, consulta PostgreSQL y ensambla un bloque en formato Markdown con el estado metodológico confirmado hasta ese instante (título, ODS, problema central, preguntas, objetivos, hipótesis, variables e indicadores).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Resuelve el Olvido del Contexto:** Al redactar las hipótesis en `P10`, el agente necesita conocer exactamente los objetivos de `P09`, la formulación de `P07` y el título de `P04`. En lugar de exigir que el usuario copie y pegue datos anteriores, este módulo los recupera automáticamente de la base de datos.
* **Datos Verificados:** Solo inyecta información de pasos que ya fueron formalmente completados y validados.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Consulta `PerfilInvestigacion` y sus datos principales (enfoque, ODS, unidad de análisis, periodo, lugar).
2. Consulta `ProgresoPaso` buscando los pasos completados (`P01`..`P12`).
3. Consulta `FilaConsistencia` ordenada por `orden`, extrayendo preguntas, objetivos e hipótesis.
4. Consulta `VariableInvestigacion`, `DimensionVariable` e `Indicador`.
5. Ensambla un bloque estructurado en Markdown con viñetas claras y lo retorna como cadena de texto.

## 4. Componentes y Funciones Clave
* `hidratar_contexto_proyecto(id_proyecto: str) -> str`: Ensamblador del contexto en vivo.

## 5. Relaciones con Otras Capas y Tablas
* **Modelos Consultados:** `PerfilInvestigacion`, `ProgresoPaso`, `FilaConsistencia`, `VariableInvestigacion`, `DimensionVariable`, `Indicador`.
* **Invocador:** Llamado por cada prompt metodológico en [`mcp_server/prompts/catalogo.py`](./catalogo.md).
