# 00. Índice Maestro y Mapa Completo del Código (`V1`)

Bienvenido a la documentación técnica en profundidad de **TesisMCP — Edición de Avance Capítulos 1 al 3 (`P01` a `P12`)**. Esta carpeta de documentación explica línea por línea cómo está construido el proyecto, qué patrones de diseño utiliza y cómo fluyen los datos desde el cliente MCP o la API REST hasta PostgreSQL.

---

## 1. Documentos de Estudio en esta Carpeta

1. [**01. Arquitectura en Capas y Patrones de Diseño (`01_ARQUITECTURA_Y_PATRONES_DISENO.md`)**](./01_ARQUITECTURA_Y_PATRONES_DISENO.md)
   * Explica la separación en 5 capas (*Clean/Layered Architecture*) y los 7 patrones de diseño de ingeniería de software aplicados en el código.
2. [**02. Modelo de Datos y Esquema Físico en Español (`02_MODELO_DATOS_Y_ESQUEMA.md`)**](./02_MODELO_DATOS_Y_ESQUEMA.md)
   * Explica los **15 modelos Django** y las **17 tablas físicas en PostgreSQL** (`tesis_*`), incluyendo el diagrama Entidad-Relación, las restricciones de integridad (`CheckConstraint`, `UniqueConstraint`) y los triggers de inmutabilidad en PL/pgSQL.
3. [**03. Flujo Metodológico de los Capítulos 1 al 3 (`03_FLUJO_METODOLOGICO_P01_A_P12.md`)**](./03_FLUJO_METODOLOGICO_P01_A_P12.md)
   * Recorrido detallado de los **12 pasos (`P01` a `P12`)**: qué valida cada contrato Pydantic (`SalidaP01` a `SalidaP12`) y cómo se materializan en la Matriz de Consistencia y la Matriz de Operacionalización.
4. [**04. Servidor MCP, Prompts Hidratados e Integraciones (`04_SERVIDOR_MCP_E_INTEGRACIONES.md`)**](./04_SERVIDOR_MCP_E_INTEGRACIONES.md)
   * Cómo operan las **17 herramientas MCP**, los **15 prompts dinámicos**, el puente asíncrono-síncrono (`puente_django.py`), la autenticación por token SHA-256 y los clientes HTTP hacia OpenAlex, Semantic Scholar y ALICIA (CONCYTEC).
5. [**05. Suite de Pruebas, Puerta DoD y Defensa Docente (`05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md`)**](./05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md)
   * Desglose de las 34 pruebas automatizadas, la puerta `verify_project.py` y un banco de preguntas y respuestas técnicas para sustentar el avance frente al docente.
6. [**06. Evaluación Técnica Imparcial: PostgreSQL vs. NoSQL (`06_EVALUACION_POSTGRESQL_VS_NOSQL.md`)**](./06_EVALUACION_POSTGRESQL_VS_NOSQL.md)
   * Análisis neutral de arquitectura de datos (Relacional vs. Documental vs. Grafos vs. Clave-Valor), matriz de decisión ponderada, enfoque multimodelo (`JSONB`) y guía de defensa ante el profesor.
7. [**07. Informe Base del Proyecto (Capítulos 1 al 3: `07_INFORME_BASE_SEMANA_10.md`)**](./07_INFORME_BASE_SEMANA_10.md)
   * Informe académico y técnico formal del proyecto, con detalle de arquitectura, catálogo metodológico y justificaciones.
8. [**08. Arquitectura Evolutiva Frontend–Backend (`08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md`)**](./08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md)
   * Decisión canónica para conectar el prototipo React con `V1`, evolucionar de P01–P12 a capacidades posteriores y evitar ramas de producto divergentes.
9. [**09. Relevo para la Implementación Frontend–Backend (`09_HANDOFF_IMPLEMENTACION_FRONTEND.md`)**](./09_HANDOFF_IMPLEMENTACION_FRONTEND.md)
   * Estado comprobado, límites, primer recorrido vertical P01, criterios de aceptación y orden de lectura para continuar la implementación en otro chat.
10. [**10. Convenciones de Nomenclatura en Español (`10_CONVENCIONES_NOMENCLATURA.md`)**](./10_CONVENCIONES_NOMENCLATURA.md)
   * Regla permanente, inventario clasificado, contrato HTTP canónico y compatibilidad histórica pendiente de retirar.
11. [**Diagramas Oficiales en Blanco y Negro (`docs/diagramas/`)**](./diagramas/00_arquitectura_sistema.png)
   * Diagrama general de Arquitectura del Sistema + los 7 diagramas metodológicos (`01` a `07`) en formato monocromático de alta resolución y archivos editables `.drawio` compatibles con [diagrams.net](https://app.diagrams.net/): Arquitectura, Ishikawa, Lean Canvas, FODA, Casos de Uso UML, Modelo Conceptual ER, Modelo Lógico 3NF y DER Físico de 17 Tablas.

---

## 2. Mapa Completo del Repositorio (Archivo por Archivo)

```text
V1/
├── README.md                                 # Resumen ejecutivo y comandos de arranque rápido
├── compose.yaml                              # Orquestación Docker (PostgreSQL 16 + Backend + MCP)
├── Dockerfile                                # Imagen Python 3.14 para backend y servidor MCP
├── pytest.ini                                # Configuración de pytest apuntando a config.settings
├── requirements-backend.txt                  # Dependencias limpias (Django, Ninja, Pydantic, SDK MCP, httpx)
├── scripts/
│   └── verify_project.py                     # Puerta determinista DoD (7 auditorías automatizadas)
│
├── docs/                                     # DOCUMENTACIÓN Y GUÍAS DE ESTUDIO
│   ├── 00_INDICE_GUIA_ESTUDIO.md             # Este índice maestro
│   ├── 01_ARQUITECTURA_Y_PATRONES_DISENO.md  # Arquitectura en 5 capas y 7 patrones de software
│   ├── 02_MODELO_DATOS_Y_ESQUEMA.md  # 15 modelos, 17 tablas tesis_* y triggers
│   ├── 03_FLUJO_METODOLOGICO_P01_A_P12.md    # Contratos Pydantic y pasos metodológicos P01-P12
│   ├── 04_SERVIDOR_MCP_E_INTEGRACIONES.md    # 17 herramientas MCP y 15 prompts dinámicos
│   ├── 05_PRUEBAS_AUDITORIA_Y_DEFENSA_DOCENTE.md # 34 pruebas pytest y defensa académica
│   ├── 06_EVALUACION_POSTGRESQL_VS_NOSQL.md  # Análisis comparativo neutral de BD
│   ├── 07_INFORME_BASE_SEMANA_10.md          # Informe base formal de entrega
│   ├── 08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md # Arquitectura incremental React + Django
│   ├── 09_HANDOFF_IMPLEMENTACION_FRONTEND.md  # Relevo operativo y primer hito P01
│   ├── 10_CONVENCIONES_NOMENCLATURA.md # Contrato canónico y excepciones verificadas
│   └── diagramas/                            # 7 diagramas oficiales en PNG y editable .drawio
│       ├── 01_ishikawa_situacion_problematica.png / .drawio
│       ├── 02_lean_canvas_tesismcp.png / .drawio
│       ├── 03_foda_diagnostico_estrategico.png / .drawio
│       ├── 04_casos_uso_sistema.png / .drawio
│       ├── 05_modelo_conceptual_er.png / .drawio
│       ├── 06_modelo_logico_relacional.png / .drawio
│       └── 07_der_modelo_fisico_17_tablas.png / .drawio
│
├── backend/                                  # NÚCLEO BACKEND (DJANGO 5.2 + DJANGO NINJA)
│   ├── manage.py                             # Punto de entrada CLI de administración Django
│   ├── config/
│   │   ├── settings.py                       # Configuración BD (tesismcp) y apps
│   │   ├── urls.py                           # Enrutador raíz (/salud/, /admin/ y /api/v1/)
│   │   ├── api.py                            # Instancia NinjaAPI y router de proyectos
│   │   └── wsgi.py                           # Punto de entrada WSGI para despliegue
│   │
│   └── thesis/                               # APLICACIÓN DE DOMINIO ACADÉMICO
│       ├── admin.py                          # Panel administrativo con protección append-only
│       ├── catalogo_pasos.py                 # Catálogo declarativo de los 12 pasos (P01-P12, Cap. 1-3)
│       │
│       ├── api/
│       │   └── proyectos.py                  # Endpoints REST para proyectos, pasos y revisión docente
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
│       │   └── 0002_integridad_esquema.py # Renombrado M2M, constraints tesis_* y triggers PL/pgSQL
│       │   └── 0003_normalizacion_estados.py # Estados, roles y acciones persistidos en español
│       │
│       ├── services/                         # CAPA DE SERVICIOS DE DOMINIO (LÓGICA DE NEGOCIO)
│       │   ├── errores.py                    # Excepción de dominio y códigos públicos
│       │   ├── acceso.py                     # Control de acceso por rol (TESISTA vs ASESOR)
│       │   ├── autenticacion_mcp.py          # Emisión, hash SHA-256 y validación de tokens MCP
│       │   ├── proyectos.py                  # Creación de proyecto y perfil; capítulos/pasos nacen al usarse
│       │   ├── contratos_pasos.py            # Contratos Pydantic estrictos (SalidaP01 a SalidaP12)
│       │   ├── pasos.py                      # Guardado transaccional de pasos con control optimista
│       │   ├── materializadores_pasos/
│       │   │   ├── __init__.py               # Exportador del materializador de capítulos 1 al 3
│       │   │   ├── registro.py               # Registro de estrategias por código de paso
│       │   │   └── consistencia.py           # Materializa P01-P12 en tablas relacionales y Markdown
│       │   ├── revisiones.py                 # Máquina de estados de revisión del asesor y observaciones
│       │   ├── exploracion.py                # Registro y exploración inicial de idea (OpenAlex)
│       │   ├── descubrimiento.py             # Búsqueda de metadatos en Semantic Scholar
│       │   ├── descubrimiento_peru.py        # Búsqueda en ALICIA CONCYTEC y filiación peruana
│       │   ├── geografia.py                  # Inferencia de alcance geográfico (Perú/Región/Internacional)
│       │   └── exportaciones.py              # Exportador de borrador Markdown de los Capítulos 1 al 3
│       │
│       ├── integrations/                     # ADAPTADORES HTTP EXTERNOS (GATEWAYS)
│       │   ├── openalex.py                   # Cliente HTTP hacia API de OpenAlex
│       │   ├── semantic_scholar.py           # Cliente HTTP hacia API de Semantic Scholar
│       │   ├── alicia.py                     # Cliente HTTP hacia repositorio nacional ALICIA
│       │   └── articulos_peru.py              # Filtro de artículos con filiación institucional peruana
│       │
│       └── tests/                            # SUITE AUTOMATIZADA (34 PRUEBAS PYTEST)
│           ├── test_salud.py                # Salud de API y modelo Usuario
│           ├── test_primer_corte.py           # Flujo vertical P01, bloqueo optimista e inmutabilidad BD
│           ├── test_descubrimiento.py             # Exploración de ideas y Semantic Scholar
│           ├── test_descubrimiento_peru.py        # Búsqueda nacional ALICIA y filiación peruana
│           ├── test_flujo_academico.py         # Ciclo de revisión docente, observaciones y guardia P13
│           ├── test_pasos_ampliados.py        # Validación de pasos P01 a P12 y bloqueo de capítulos 4-7
│           ├── test_prompts_mcp.py           # Registro e hidratación de los 15 prompts MCP
│           └── pasos_ampliados/
│               ├── conftest.py               # Fixtures compartidos para pruebas de capítulos
│               └── test_capitulo3.py          # Pruebas profundas de Matriz de Consistencia y Variables
│
└── mcp_server/                               # SERVIDOR MODEL CONTEXT PROTOCOL (MCPSERVER)
    ├── server.py                             # Servidor principal: herramientas base y registro de módulos
    ├── herramientas_proyecto.py              # Herramientas MCP de proyecto, pasos P01-P12 y asesoría
    ├── puente_django.py                      # Puente seguro entre el SDK MCP y el ORM síncrono
    ├── prueba_local.py                       # Simulación E2E interactiva de los 12 pasos y 3 capítulos
    ├── demostracion/
    │   ├── datos_caso.py                     # Cargas metodológicas de prueba para P01-P12
    │   └── soporte.py                        # Utilidades de invocación MCP para simulación
    └── prompts/
        ├── catalogo.py                       # Registro de los 15 prompts en MCPServer
        ├── hidratacion.py                    # Hidratación de contexto en vivo desde PostgreSQL
        ├── roles.py                          # 3 prompts de rol (Asesor, Investigador, Revisor)
        └── plantillas/
            ├── __init__.py                   # Ensamblador de plantillas de Capítulos 1 al 3
            ├── capitulo_1.py                  # Plantillas de prompts para P01 a P05
            ├── capitulo_2.py                  # Plantillas de prompts para P06 a P08
            └── capitulo_3.py                  # Plantillas de prompts para P09 a P12
```
