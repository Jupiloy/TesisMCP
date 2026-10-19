# TesisMCP — Avance de Primera Semana (Capítulos 1 al 3: P01 a P12)

Esta carpeta contiene la implementación funcional en español de **TesisMCP** acotada al **Avance de Primera Semana (Capítulos 1 al 3)** del Curso Integrador I: Sistemas - Software.

Conserva la arquitectura desacoplada real del proyecto (servidor MCP sobre `FastMCP`, API REST con Django Ninja, validación estricta con contratos Pydantic `SalidaEstricta` (`extra="forbid"`), control de concurrencia optimista `lock_version`, Matriz de Consistencia relacional, Matriz de Operacionalización de variables y máquina de estados de revisión del asesor con historial inmutable *append-only* mediante triggers PL/pgSQL y tokens SHA-256), delimitando el alcance a los primeros tres capítulos metodológicos.

---

## 📚 Documentación Técnica en Profundidad (`docs/`)

Para estudiar a fondo cómo está programado cada módulo, patrón de diseño y tabla de este avance, revisa la subcarpeta [`docs/`](./docs/00_INDICE_GUIA_ESTUDIO.md):

1. [**00. Índice Maestro y Mapa Completo del Código**](./docs/00_INDICE_GUIA_ESTUDIO.md)
2. [**01. Arquitectura en Capas y Patrones de Diseño Senior**](./docs/01_ARQUITECTURA_Y_PATRONES_DISENO.md)
3. [**02. Modelo de Datos y Esquema Físico en Español (15 Modelos / 17 Tablas)**](./docs/02_MODELO_DATOS_Y_ESQUEMA_ESPANOL.md)
4. [**03. Flujo Metodológico Paso a Paso: Capítulos 1 al 3 (`P01` a `P12`)**](./docs/03_FLUJO_METODOLOGICO_P01_A_P12.md)
5. [**04. Servidor MCP (`FastMCP`), Prompts Hidratados e Integraciones Científicas**](./docs/04_SERVIDOR_MCP_E_INTEGRACIONES.md)
6. [**05. Suite de Pruebas, Puerta DoD y Guía de Defensa Docente**](./docs/05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md)
7. [**06. Evaluación Técnica Imparcial: PostgreSQL vs. NoSQL**](./docs/06_EVALUACION_POSTGRESQL_VS_NOSQL.md)

---

## 📌 Alcance Funcional Implementado (Capítulos 1 al 3)

| Dimensión | Implementado en este Avance | Planificado para Siguientes Entregas (Cap. 4–7) |
| :--- | :--- | :--- |
| **Capítulos habilitados** | **Capítulos 1, 2 y 3** (`CheckConstraint 1..3`) | Capítulos 4 (Literatura), 5 (Marco Teórico), 6 (Metodología) y 7 (Instrumentos) |
| **Pasos metodológicos** | **12 pasos (`P01` a `P12`)** con contratos Pydantic estrictos | Pasos `P13` a `P32` (PRISMA, marco conceptual, diseño e instrumentos) |
| **Modelos Django / Tablas** | **15 modelos relacionales** (17 tablas físicas `tesis_*` en español) | Tablas de procesamiento PDF/GROBID/OCR, manuscritos e instrumentos |
| **Migraciones** | **2 migraciones limpias en español** (`0001_inicial`, `0002_inmutabilidad_espanol`) | Migraciones de capítulos posteriores |
| **Herramientas MCP** | **17 herramientas MCP** (catálogo, proyecto, exploración OpenAlex/Semantic Scholar/ALICIA Perú, pasos `P01`–`P12` y revisión docente) | Herramientas de ingesta PDF, GROBID, OCR y enlaces de evidencia a página física |
| **Prompts MCP** | **15 prompts MCP** (12 plantillas `P01`–`P12` hidratadas desde PostgreSQL + 3 roles) | Plantillas `P13`–`P32` |

### Catálogo Metodológico Activo (`P01` a `P12`)

1. **Capítulo 1 — Elección del Tema y Alcance:**
   - `P01` (**Mapa de Temas y Problema**): 5 a 10 temas potenciales con pros, contras, viabilidad preliminar y tema preseleccionado (`SalidaP01`).
   - `P02` (**Tipo de Investigación**): Enfoque (`CUANTITATIVO`, `CUALITATIVO`, `MIXTO`), alcance, diseño y justificación (`SalidaP02`).
   - `P03` (**Población, Muestra y ODS**): Descripción de población, tamaño de muestra ($> 0$) y meta ODS validada por expresión regular `ODS-XX:X.X` (`SalidaP03`).
   - `P04` (**Título de Investigación**): Título oficial con variable independiente, variable dependiente, unidad de análisis, contexto espacial y periodo temporal (`SalidaP04`).
   - `P05` (**Alcance de la Investigación**): Alcance definido, justificación, delimitaciones y limitaciones (`SalidaP05`).
2. **Capítulo 2 — Realidad Problemática y Justificación:**
   - `P06` (**Planteamiento del Problema**): Diagnóstico estructurado en los 6 bloques `CA-S-P-CO-CC-PC` (`SalidaP06`).
   - `P07` (**Formulación del Problema**): Pregunta general y preguntas específicas (`SalidaP07`).
   - `P08` (**Justificación de la Investigación**): Justificación teórica, práctica, metodológica y social (`SalidaP08`).
3. **Capítulo 3 — Objetivos, Preguntas, Hipótesis y Operacionalización:**
   - `P09` (**Objetivos e Inicio de Matriz de Consistencia**): Objetivo general, objetivos específicos y creación de filas `GENERAL` y `SPECIFIC` en `FilaConsistencia` (`SalidaP09`).
   - `P10` (**Preguntas Específicas e Hipótesis**): Hipótesis general, nula y específicas sincronizadas en `FilaConsistencia` (`SalidaP10`).
   - `P11` (**Definición Conceptual y Operacional de Variables**): Materializa `VariableInvestigacion` (`VI` y `VD`) y cruces en `VariableFilaConsistencia` (`SalidaP11`).
   - `P12` (**Matriz de Operacionalización**): Materializa `DimensionVariable` e `Indicador` con fórmula, unidad de medida, escala e instrumento (`SalidaP12`).

---

## 🏗️ Arquitectura del Avance

```mermaid
flowchart TD
    subgraph Clientes["Capas de Cliente"]
        WebUI["💻 Panel Admin y Clientes HTTP<br>(Django Admin - 15 modelos)"]
        AIClient["🤖 Cliente LLM Asistido<br>(Claude Desktop / Cursor IDE)"]
    end

    subgraph Protocolo["Capa de Comunicación"]
        MCP["🔌 Servidor MCP (FastMCP)<br>17 herramientas + 15 prompts (P01-P12 + 3 roles)"]
        REST["🌐 API REST OpenAPI<br>/api/ (Django Ninja)"]
    end

    subgraph Backend["Núcleo Transaccional (Capítulos 1 al 3)"]
        Bridge["django_bridge.py + mcp_auth.py<br>(Token SHA-256)"]
        Services["thesis.services<br>(Contratos P01-P12 + consistency.py + reviews.py)"]
        Discovery["Integradores de Exploración<br>(OpenAlex, Semantic Scholar, ALICIA Perú)"]
    end

    subgraph Persistencia["PostgreSQL 16 (tesismcp_reducido_docente)"]
        DB[("📦 15 Modelos / 17 Tablas Físicas en Español<br>Matriz de Consistencia + Variables + Capítulos 1..3")]
    end

    AIClient <-->|JSON-RPC stdio| MCP
    MCP --> Bridge
    Bridge --> Services
    WebUI --> Services
    AIClient <-->|HTTP JSON| REST
    REST --> Services
    Services --> Discovery
    Services --> DB
```

---

## ⚡ Guía de Inicio Rápido

### 1. Aplicar Migraciones y Ejecutar Pruebas
Usa la base de datos aislada `tesismcp_reducido_docente` en la instancia local de PostgreSQL:

```bash
cd version_reducida_docente
DJANGO_DEBUG=1 ../.venv/bin/python backend/manage.py migrate
DJANGO_DEBUG=1 ../.venv/bin/python -m pytest --reuse-db -q
```

### 2. Ejecutar la Simulación End-to-End del Servidor MCP (Capítulos 1 al 3)
Recorre los 12 pasos (`P01` a `P12`), demuestra el bloqueo de pasos fuera de alcance (`P13`), materializa la Matriz de Consistencia y la Matriz de Operacionalización en PostgreSQL, y ejecuta el ciclo completo de revisión y aprobación del asesor en los Capítulos 1 al 3:

```bash
cd version_reducida_docente
DJANGO_DEBUG=1 ../.venv/bin/python mcp_server/test_local.py
```

### 3. Ejecutar la Puerta Determinista de Verificación
Comprueba salud de Django, migraciones, esquema físico español en PostgreSQL (17 tablas `tesis_*`), suite `pytest`, higiene de archivos, conteos exactos (15 modelos, 2 migraciones, 12 pasos, 17 herramientas MCP y 15 prompts) y contratos Pydantic:

```bash
cd version_reducida_docente
python3 scripts/verify_project.py
```
