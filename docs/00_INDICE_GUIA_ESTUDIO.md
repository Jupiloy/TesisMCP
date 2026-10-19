# 00. Índice Maestro y Mapa Completo del Código (`version_reducida_docente`)

Bienvenido a la documentación técnica en profundidad de **TesisMCP — Edición de Avance Capítulos 1 al 3 (`P01` a `P12`)**. Esta carpeta de documentación explica línea por línea cómo está construido el proyecto, qué patrones de diseño utiliza y cómo fluyen los datos desde el cliente MCP o la API REST hasta PostgreSQL.

---

## 1. Documentos de Estudio en esta Carpeta

1. [**01. Arquitectura en Capas y Patrones de Diseño (`01_ARQUITECTURA_Y_PATRONES_DISENO.md`)**](./01_ARQUITECTURA_Y_PATRONES_DISENO.md)
   * Explica la separación en 5 capas (*Clean/Layered Architecture*) y los 7 patrones de diseño de ingeniería de software aplicados en el código.
2. [**02. Modelo de Datos y Esquema Físico en Español (`02_MODELO_DATOS_Y_ESQUEMA_ESPANOL.md`)**](./02_MODELO_DATOS_Y_ESQUEMA_ESPANOL.md)
   * Explica los **15 modelos Django** y las **17 tablas físicas en PostgreSQL** (`tesis_*`), incluyendo el diagrama Entidad-Relación, las restricciones de integridad (`CheckConstraint`, `UniqueConstraint`) y los triggers de inmutabilidad en PL/pgSQL.
3. [**03. Flujo Metodológico de los Capítulos 1 al 3 (`03_FLUJO_METODOLOGICO_P01_A_P12.md`)**](./03_FLUJO_METODOLOGICO_P01_A_P12.md)
   * Recorrido detallado de los **12 pasos (`P01` a `P12`)**: qué valida cada contrato Pydantic (`SalidaP01` a `SalidaP12`) y cómo se materializan en la Matriz de Consistencia y la Matriz de Operacionalización.
4. [**04. Servidor MCP, Prompts Hidratados e Integraciones (`04_SERVIDOR_MCP_E_INTEGRACIONES.md`)**](./04_SERVIDOR_MCP_E_INTEGRACIONES.md)
   * Cómo operan las **17 herramientas MCP**, los **15 prompts dinámicos**, el puente asíncrono-síncrono (`django_bridge.py`), la autenticación por token SHA-256 y los clientes HTTP hacia OpenAlex, Semantic Scholar y ALICIA (CONCYTEC).
5. [**05. Suite de Pruebas, Puerta DoD y Defensa Docente (`05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md`)**](./05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md)
   * Desglose de las 32 pruebas automatizadas, la puerta `verify_project.py` y un banco de preguntas y respuestas técnicas para sustentar el avance frente al docente.
6. [**06. Evaluación Técnica Imparcial: PostgreSQL vs. NoSQL (`06_EVALUACION_POSTGRESQL_VS_NOSQL.md`)**](./06_EVALUACION_POSTGRESQL_VS_NOSQL.md)
   * Análisis neutral de arquitectura de datos (Relacional vs. Documental vs. Grafos vs. Clave-Valor), matriz de decisión ponderada, enfoque multimodelo (`JSONB`) y guía de defensa ante el profesor.

---

## 2. Mapa Completo del Repositorio (Archivo por Archivo)

```text
version_reducida_docente/
├── README.md                                 # Resumen ejecutivo y comandos de arranque rápido
├── compose.yaml                              # Orquestación Docker (PostgreSQL 16 + Backend + MCP)
├── Dockerfile                                # Imagen Python 3.14 para backend y servidor MCP
├── pytest.ini                                # Configuración de pytest apuntando a config.settings
├── requirements-backend.txt                  # Dependencias limpias (Django, Ninja, Pydantic, SDK MCP, httpx)
├── scripts/
│   └── verify_project.py                     # Puerta determinista DoD (7 auditorías automatizadas)
│
├── backend/                                  # NÚCLEO BACKEND (DJANGO 5.2 + DJANGO NINJA)
│   ├── manage.py                             # Punto de entrada CLI de administración Django
│   ├── config/
│   │   ├── settings.py                       # Configuración BD (tesismcp_reducido_docente) y apps
│   │   ├── urls.py                           # Enrutador raíz (/health/, /admin/ y /api/v1/)
│   │   ├── api.py                            # Instancia NinjaAPI, endpoint /health y router de proyectos
│   │   └── wsgi.py                           # Punto de entrada WSGI para despliegue
│   │
│   └── thesis/                               # APLICACIÓN DE DOMINIO ACADÉMICO
│       ├── admin.py                          # Panel administrativo con protección append-only
│       ├── step_catalogue.py                 # Catálogo declarativo de los 12 pasos (P01-P12, Cap. 1-3)
│       │
│       ├── api/
│       │   └── projects.py                   # Endpoints REST para proyectos, pasos y revisión docente
│       │
│       ├── models/                           # CAPA DE PERSISTENCIA (15 MODELOS -> 17 TABLAS tesis_*)
│       │   ├── __init__.py                   # Exportación unificada y traducción física al español
│       │   ├── accounts.py                   # Usuario y TokenAccesoMcp (SHA-256)
│       │   ├── projects.py                   # Proyecto (con lock_version) y ParticipanteProyecto
│       │   ├── research.py                   # PerfilInvestigacion, FilaConsistencia, VariableInvestigacion,
│       │   │                                 # VariableFilaConsistencia, DimensionVariable, Indicador
│       │   └── chapters.py                   # ProgresoPaso, Capitulo (1..3), RevisionCapitulo,
│       │                                     # ComentarioRevision, EventoRevision
│       │
│       ├── migrations/                       # MIGRACIONES FÍSICAS CONSOLIDADAS
│       │   ├── 0001_inicial.py               # Creación de las 15 entidades y sus tablas tesis_*
│       │   └── 0002_inmutabilidad_espanol.py # Renombrado M2M, constraints tesis_* y triggers PL/pgSQL
│       │
│       ├── services/                         # CAPA DE SERVICIOS DE DOMINIO (LÓGICA DE NEGOCIO)
│       │   ├── errors.py                     # Jerarquía de excepciones (ErrorDominio, ErrorConflicto...)
│       │   ├── access.py                     # Control de acceso por rol (TESISTA vs ASESOR)
│       │   ├── mcp_auth.py                   # Emisión, hash SHA-256 y validación de tokens MCP
│       │   ├── projects.py                   # Creación de proyecto y perfil; capítulos/pasos nacen al usarse
│       │   ├── step_contracts.py             # Contratos Pydantic estrictos (SalidaP01 a SalidaP12)
│       │   ├── steps.py                      # Guardado transaccional de pasos con control optimista
│       │   ├── step_materializers/
│       │   │   ├── __init__.py               # Exportador del materializador de capítulos 1 al 3
│       │   │   └── consistency.py            # Materializa P01-P12 en tablas relacionales y Markdown
│       │   ├── reviews.py                    # Máquina de estados de revisión del asesor y observaciones
│       │   ├── exploration.py                # Registro y exploración inicial de idea (OpenAlex)
│       │   ├── discovery.py                  # Búsqueda de metadatos en Semantic Scholar
│       │   ├── discovery_peru.py             # Búsqueda en ALICIA CONCYTEC y filiación peruana
│       │   ├── geography.py                  # Inferencia de alcance geográfico (Perú/Región/Internacional)
│       │   └── exports.py                    # Exportador de borrador Markdown de los Capítulos 1 al 3
│       │
│       ├── integrations/                     # ADAPTADORES HTTP EXTERNOS (GATEWAYS)
│       │   ├── openalex.py                   # Cliente HTTP hacia API de OpenAlex
│       │   ├── semantic_scholar.py           # Cliente HTTP hacia API de Semantic Scholar
│       │   ├── alicia.py                     # Cliente HTTP hacia repositorio nacional ALICIA
│       │   └── peru_articles.py              # Filtro de artículos con filiación institucional peruana
│       │
│       └── tests/                            # SUITE AUTOMATIZADA (32 PRUEBAS PYTEST)
│           ├── test_health.py                # Salud de API y modelo Usuario
│           ├── test_first_slice.py           # Flujo vertical P01, bloqueo optimista e inmutabilidad BD
│           ├── test_discovery.py             # Exploración de ideas y Semantic Scholar
│           ├── test_discovery_peru.py        # Búsqueda nacional ALICIA y filiación peruana
│           ├── test_academic_flow.py         # Ciclo de revisión docente, observaciones y guardia P13
│           ├── test_extended_steps.py        # Validación de pasos P01 a P12 y bloqueo de capítulos 4-7
│           ├── test_mcp_prompts.py           # Registro e hidratación de los 15 prompts MCP
│           └── extended_steps/
│               ├── conftest.py               # Fixtures compartidos para pruebas de capítulos
│               └── test_chapter3.py          # Pruebas profundas de Matriz de Consistencia y Variables
│
└── mcp_server/                               # SERVIDOR MODEL CONTEXT PROTOCOL (MCPSERVER)
    ├── server.py                             # Servidor principal: herramientas base y registro de módulos
    ├── project_tools.py                      # Herramientas MCP de proyecto, pasos P01-P12 y asesoría
    ├── django_bridge.py                      # Puente seguro entre el SDK MCP y el ORM síncrono
    ├── test_local.py                         # Simulación E2E interactiva de los 12 pasos y 3 capítulos
    ├── demo/
    │   ├── case_data.py                      # Payloads metodológicos de prueba para P01-P12
    │   └── support.py                        # Utilidades de invocación MCP para simulación
    └── prompts/
        ├── catalog.py                        # Registro de los 15 prompts en MCPServer
        ├── hydration.py                      # Hidratación de contexto en vivo desde PostgreSQL
        ├── roles.py                          # 3 prompts de rol (Asesor, Investigador, Revisor)
        └── templates/
            ├── __init__.py                   # Ensamblador de plantillas de Capítulos 1 al 3
            ├── chapter_1.py                  # Plantillas de prompts para P01 a P05
            ├── chapter_2.py                  # Plantillas de prompts para P06 a P08
            └── chapter_3.py                  # Plantillas de prompts para P09 a P12
```
