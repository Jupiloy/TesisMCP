# 06. Evaluación Técnica Imparcial: PostgreSQL (Relacional) vs. NoSQL en TesisMCP

Este documento presenta un análisis de arquitectura de datos riguroso, neutral e imparcial para evaluar si el sistema **TesisMCP** debe basarse en una **Base de Datos Relacional (PostgreSQL)**, una **Base de Datos No Relacional (NoSQL: Documental, Grafo, Clave-Valor)** o un **Enfoque Híbrido**.

---

## 1. El Dilema Técnico Central en TesisMCP

El desarrollo de un sistema asistido por Modelos de Lenguaje (LLMs) para la formulación de tesis enfrenta una tensión fundamental de ingeniería:

```text
               ┌────────────────────────────────────────────────────────┐
               │              EL DILEMA DE DATOS EN TESISMCP            │
               └──────────────────────────┬─────────────────────────────┘
                                          │
              ┌───────────────────────────┴───────────────────────────┐
              ▼                                                       ▼
  CARGA DOCUMENTAL DINÁMICA                              CARGA RELACIONAL METODOLÓGICA
• Salidas no estructuradas del LLM                      • Matriz de Consistencia biunívoca
• Payloads JSON variables por paso                      • Integridad referencial (Objetivo <-> Variable)
• Exploración libre de literatura                       • Control de concurrencia optimista (lock_version)
• Requisitos típicos de NoSQL Documental                • Auditoría inmutable legal/docente (Triggers)
                                                        • Requisitos típicos de RDBMS (ACID)
```

1. **La Tentación NoSQL:** Los LLMs devuelven JSON. En un enfoque superficial, almacenar documentos JSON en una base de datos NoSQL documental como MongoDB parece natural, flexible y rápido de implementar en una primera semana.
2. **La Realidad Metodológica de una Tesis:** Una tesis universitaria no es un blog ni una colección arbitraria de documentos. La metodología científica exige **coherencia estricta**:
   * Cada pregunta específica debe corresponder a un objetivo específico y a una hipótesis específica.
   * Cada variable debe descomponerse en dimensiones, y cada dimensión en indicadores medibles.
   * Si se altera una variable o se elimina un objetivo, el sistema no puede dejar registros huérfanos ni inconsistencias conceptuales.

---

## 2. Análisis Imparcial de Candidatos (Pros, Contras y Modos de Falla)

### Opción A: PostgreSQL (RDBMS Objeto-Relacional con soporte Multimodelo)

* **Ventajas Técnicas:**
  1. **Integridad Referencial y Restricciones Físicas:** Soporta `FOREIGN KEY` con `PROTECT`, `CheckConstraint` (como obligar a que el número de capítulo esté entre 1 y 3) y `UniqueConstraint` condicionales (un único asesor activo por proyecto con `Q(role="ADVISOR", active=True)`).
  2. **Transaccionalidad ACID Estricta:** En `guardar_paso_servicio`, la materialización relacional, la creación de la revisión, la actualización de `ProgresoPaso` y el incremento de `lock_version` ocurren dentro de `transaction.atomic()`. O se persiste todo o no se persiste nada.
  3. **Capacidades Documentales Nativas (`JSONB` + Índices GIN):** PostgreSQL almacena JSON descompuesto en formato binario (`JSONB`), permitiendo consultas e indexación dentro de claves internas sin sacrificar el esquema relacional.
  4. **Garantía de Inmutabilidad en el Motor (PL/pgSQL Triggers):** Permite disparadores a nivel de motor (`BEFORE UPDATE OR DELETE`) como `tesis_rechazar_cambio_historial()` para que nadie, ni siquiera un administrador con acceso SQL, pueda alterar revisiones o bitácoras pasadas.
  5. **Búsqueda Semántica Vectorial Unificada (`pgvector`):** En la versión completa, soporta vectores de embeddings sin necesidad de incorporar otra base de datos como Pinecone o Milvus.
* **Desventajas y Limitaciones Reales:**
  1. **Mayor Fricción en Modificaciones de Esquema:** Agregar o renombrar columnas requiere crear y validar migraciones formales (`manage.py makemigrations`), a diferencia de un esquema *schemaless*.
  2. **Escalamiento Horizontal Complejo:** El escalamiento natural de PostgreSQL es vertical (CPU/RAM). Para sharding horizontal distribuido de escritura se requieren extensiones avanzadas como Citus, mientras que bases de datos como Cassandra o DynamoDB nacieron distribuidas.

---

### Opción B: Base de Datos NoSQL Documental (ej. MongoDB, CouchDB)

* **Ventajas Técnicas:**
  1. **Correspondencia Natural con Salidas JSON:** El payload generado por el agente IA puede insertarse como un documento BSON directamente sin etapa intermedia de mapeo objeto-relacional.
  2. **Flexibilidad Radical de Esquema (*Schema-on-read*):** Si el paso `P06` añade un nuevo campo no planificado (ej. `contexto_regional`), la base de datos lo almacena sin necesidad de correr migraciones ni alterar tablas previas.
  3. **Lecturas Rápidas de Documentos Completos:** Consultar un capítulo completo con todos sus pasos anidados se resuelve en una sola lectura sin sentencias `JOIN`.
* **Desventajas y Riesgos Críticos para TesisMCP:**
  1. **Ausencia de Restricciones Relacionales en el Motor:** MongoDB no cuenta con `CheckConstraint` entre colecciones ni llaves foráneas con validación referencial en motor. Si se borra una variable o se edita un objetivo, la prevención de datos huérfanos recae al 100 % en el código de la aplicación (vulnerable a bugs en despliegues concurrentes).
  2. **Transacciones Multidocumento Costosas:** Aunque MongoDB soporta transacciones ACID multidocumento desde la versión 4.0, tienen una penalización de latencia significativa y requieren configuración de Replica Sets obligatoria.
  3. **Imposibilidad de Triggers Nativos a Nivel de Kernel:** No existe un equivalente directo de disparadores PL/pgSQL transaccionales que bloqueen `UPDATE` y `DELETE` de manera determinista a nivel de motor de almacenamiento.

---

### Opción C: Base de Datos NoSQL en Grafos (ej. Neo4j)

* **Ventajas Técnicas:**
  1. **Modelado Natural de Redes de Conocimiento:** Ideal para mapear redes de citas académicas, ontologías de conceptos y genealogía de antecedentes científicos.
* **Desventajas y Limitaciones:**
  1. **Pésimo Ajuste para Gestión Transaccional Tradicional:** Autenticación de usuarios, permisos, roles, control de versiones optimista y flujos de aprobación de capítulos se vuelven innecesariamente complejos y lentos en un motor de grafos.
  2. **Sobrecarga de Infraestructura:** Operar un cluster de Neo4j junto al backend introduce una carga operativa desproporcionada para el alcance del proyecto.

---

### Opción D: Base de Datos Clave-Valor / En Memoria (ej. Redis)

* **Rol Técnico Real:**
  * No es un sustituto de la base de datos principal, sino una **capa complementaria** de caché de sesiones, rate-limiting de peticiones MCP y cola de tareas asíncronas (Celery).

---

## 3. Matriz de Decisión Ponderada

Evaluación técnica sobre una escala de 1 a 5 (donde 5 representa la idoneidad máxima para los requerimientos de TesisMCP):

| Criterio Técnico | Peso | PostgreSQL | NoSQL Documental (MongoDB) | NoSQL Grafo (Neo4j) | Justificación del Peso en TesisMCP |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Integridad Referencial y Consistencia** | 25% | **5 / 5** | 2 / 5 | 3 / 5 | Crítico: la Matriz de Consistencia exige coherencia matemática entre objetivos, variables e indicadores. |
| **Transaccionalidad ACID en Guardado** | 20% | **5 / 5** | 3 / 5 | 3 / 5 | Crítico: guardar un paso altera progreso, perfil, matriz y revisión en una sola unidad atómica. |
| **Flexibilidad para Payloads JSON de LLM** | 15% | **4 / 5** | **5 / 5** | 2 / 5 | Importante: resuelto en PostgreSQL mediante columnas nativas `JSONB` y validación Pydantic previa. |
| **Auditoría e Inmutabilidad en Motor** | 15% | **5 / 5** | 2 / 5 | 2 / 5 | Alto: las revisiones docentes no deben poder ser manipuladas ni borradas (Triggers PL/pgSQL). |
| **Búsqueda Vectorial Semántica** | 10% | **4 / 5** | 3 / 5 | 3 / 5 | Integrado en PostgreSQL vía extensión `pgvector` sin bases de datos adicionales. |
| **Simplicidad Operativa y Despliegue** | 15% | **5 / 5** | 3 / 5 | 2 / 5 | Un solo contenedor PostgreSQL en `compose.yaml` resuelve todo el stack de persistencia. |
| **Puntaje Ponderado Total** | **100%** | **4.75 / 5.0** | **2.80 / 5.0** | **2.60 / 5.0** | **PostgreSQL resulta técnica y operativamente superior.** |

---

## 4. Por qué el Enfoque Multimodelo de PostgreSQL es la Decisión Correcta

La conclusión técnica imparcial no es que *"lo relacional siempre es mejor que NoSQL"*, sino que **TesisMCP es un sistema intrínsecamente híbrido**.

PostgreSQL resuelve esta dualidad actuando como una **Base de Datos Multimodelo (Objeto-Relacional + Documental)**:

1. **La Columna Vertebral es Relacional:**
   * Las tablas `tesis_proyecto`, `tesis_participante_proyecto`, `tesis_fila_consistencia`, `tesis_variable_investigacion`, `tesis_dimension_variable` e `tesis_indicador` son relacionales porque modelan entidades con restricciones formales de unicidad, cardinalidad y llaves foráneas.
2. **La Salida de Cada Paso es Documental (`JSONB`):**
   * En `tesis_progreso_paso`, la columna `salida_json` almacena el JSON completo que ya superó su contrato Pydantic.
   * Las entidades necesarias para consultas metodológicas se materializan además en tablas relacionales; las revisiones conservan el Markdown y su SHA-256.
3. **Cero Penalización Operativa:**
   * El equipo y el despliegue gestionan **un solo motor de base de datos** en lugar de mantener sincronizadas dos bases de datos distintas (ej. PostgreSQL para usuarios y MongoDB para textos), evitando el problema de coherencia eventual (*Eventual Consistency* y *Dual Writes*).

---

## 5. Guía de Respuestas para Defensa Docente

Si el docente pregunta: *"¿Por qué usaron PostgreSQL si los modelos de lenguaje trabajan con JSON? ¿No era mejor usar MongoDB o NoSQL?"*

* **Respuesta Técnica Recomendada:**
  > *"Profesor, evaluamos objetivamente ambas alternativas. Si el sistema fuera únicamente un chat o un almacenamiento de texto libre, MongoDB habría sido suficiente. Sin embargo, TesisMCP tiene como núcleo la **Matriz de Consistencia Metodológica y la Operacionalización de Variables**: cada objetivo debe vincularse a una hipótesis, y cada variable debe descomponerse en dimensiones e indicadores con integridad referencial.*
  >
  > *Si usáramos una base documental NoSQL, el motor no puede garantizar llaves foráneas ni restricciones `CHECK` a nivel de base de datos, dejando el riesgo de inconsistencias y datos huérfanos enteramente al código. Además, PostgreSQL nos brinda un **enfoque multimodelo**: usamos tablas relacionales con transacciones ACID para las entidades formales y columnas `JSONB` nativas para almacenar las salidas dinámicas del LLM, junto con triggers en PL/pgSQL que garantizan la inmutabilidad de las revisiones docentes sin la sobrecarga de operar dos bases de datos distintas."*
