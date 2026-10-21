# Plan de continuidad de TesisMCP para otro agente de IA

> Estado inspeccionado: 21 de octubre de 2026. Este documento sirve como relevo técnico si se agota el contexto del chat actual. El código y los archivos reales en disco siempre prevalecen sobre este resumen.

## 1. Objetivo general

Continuar la integración del frontend React ubicado en `../TesisMCP_Frontend/` con el backend Django real ubicado en `V1/`, sin inventar endpoints, datos, respuestas ni capacidades futuras.

El backend implementa actualmente los capítulos 1 a 3, correspondientes a P01–P12. El frontend solo tiene conectado el primer recorrido vertical P01.

No se debe intentar completar todo el proyecto en una sola tarea. Cada hito debe implementarse, probarse y entregarse de forma independiente.

## 2. Lectura obligatoria antes de modificar código

Leer completamente y en este orden:

1. `../AGENTS.md`
2. `../GUIA_AGENTE.md`
3. `README.md`
4. `docs/08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md`
5. `docs/09_HANDOFF_IMPLEMENTACION_FRONTEND.md`
6. `docs/10_CONVENCIONES_NOMENCLATURA.md`
7. `../TesisMCP_Frontend/AGENTS.md`
8. `../TesisMCP_Frontend/CHATGPT_REVIEW.md`
9. `../TesisMCP_Frontend/src/App.tsx`
10. `../TesisMCP_Frontend/src/index.css`
11. `../TesisMCP_Frontend/src/features/metodologia/RecorridoP01.tsx`
12. `../TesisMCP_Frontend/src/lib/api/cliente.ts`
13. `../TesisMCP_Frontend/src/lib/api/contrato.mjs`

Después de leer, inspeccionar el estado real de Git y preservar todos los cambios preexistentes.

## 3. Estado funcional comprobado

### Backend `V1/`

- API Django Ninja con sesión Django y protección CSRF.
- Persistencia PostgreSQL.
- Catálogo metodológico P01–P12.
- Contratos Pydantic estrictos para las salidas de P01–P12.
- Control de concurrencia mediante `version_estado` y `version_esperada`.
- Idempotencia mediante UUID en `clave_idempotencia`.
- Revisiones de capítulos inmutables.
- Comentarios y decisiones del asesor.
- Matriz de consistencia y matriz de operacionalización materializadas relacionalmente.
- Búsquedas en OpenAlex, Semantic Scholar y proveedores peruanos.
- Exportación del borrador a DOCX.
- Servidor MCP por transporte `stdio`; no existe todavía un contrato de chat web.
- 34 pruebas automatizadas registradas en `backend/thesis/tests/`.

### Frontend `TesisMCP_Frontend/`

El recorrido P01 ya permite:

1. Consultar la sesión.
2. Consultar el catálogo.
3. Listar proyectos.
4. Crear un proyecto.
5. Abrir un proyecto.
6. Mostrar P01 y sus dependencias.
7. Editar `contenido_md` y `datos_salida`.
8. Guardar P01 con versión optimista y UUID real.
9. Recargar el proyecto desde PostgreSQL después del guardado.
10. Mostrar estados de carga, vacío, error, conflicto y éxito.
11. Mantener el chat deshabilitado con la etiqueta “Próximamente”.

No están conectados P02–P12, el flujo de revisión, las búsquedas, la exportación ni el panel del asesor.

## 4. Contrato público canónico

Todo identificador controlado por TesisMCP debe estar en español. No crear alias ingleses.

Rutas base actualmente disponibles:

```text
GET  /api/v1/sesion/actual
GET  /api/v1/metodologia/catalogo
GET  /api/v1/proyectos
POST /api/v1/proyectos
GET  /api/v1/proyectos/{id_proyecto}
PUT  /api/v1/proyectos/{id_proyecto}/pasos/{codigo_paso}
GET  /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}
POST /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/enviar
POST /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/comentarios
GET  /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/comentarios
POST /api/v1/proyectos/{id_proyecto}/comentarios/{id_comentario}/resolver
POST /api/v1/proyectos/{id_proyecto}/capitulos/{numero_capitulo}/decision
GET  /api/v1/asesor/panel
GET  /api/v1/proyectos/{id_proyecto}/exportar/borrador.docx
GET  /api/v1/proyectos/{id_proyecto}/idea/explorar
GET  /api/v1/proyectos/{id_proyecto}/descubrimiento/semantic-scholar
GET  /api/v1/proyectos/{id_proyecto}/descubrimiento/peru
POST /api/v1/proyectos/{id_proyecto}/asesor
```

El guardado de un paso usa exactamente:

```json
{
  "contenido_md": "...",
  "datos_salida": {},
  "version_esperada": 0,
  "clave_idempotencia": "uuid"
}
```

Los errores públicos contienen:

```json
{
  "codigo": "CONFLICTO_VERSION",
  "mensaje": "...",
  "detalle": "..."
}
```

Antes de consumir cualquier ruta, confirmar su forma directamente en:

- `backend/config/api.py`
- `backend/thesis/api/proyectos.py`
- El OpenAPI expuesto por Django Ninja.

## 5. Reglas que no deben romperse

- No modificar migraciones ni datos persistidos para resolver necesidades del frontend.
- No cambiar contratos backend salvo bloqueo demostrado con una prueba reproducible.
- No utilizar datos ficticios, mocks residuales ni respuestas simuladas en producción.
- No sobrescribir un `CONFLICTO_VERSION`; recargar el estado vigente.
- Generar cada `clave_idempotencia` con un UUID real.
- Usar la última `version_estado` recibida como siguiente `version_esperada`.
- No comentar el borrador vivo: los comentarios pertenecen a una revisión enviada e inmutable.
- No presentar MCP por `stdio` como un chat web conectado.
- No implementar P13–P32 hasta que existan contratos reales en el backend.
- No introducir microservicios, WebSockets o colaboración en tiempo real sin un requisito aprobado.
- Mantener la apariencia del prototipo de Figma sin conservar funcionalidades visuales falsas.
- Preservar todos los cambios preexistentes del usuario.

## 6. Plan recomendado por hitos

### Hito 0 — Consolidar el estado del repositorio y la documentación

Antes de ampliar funcionalidades:

1. Inspeccionar el estado de Git de `V1/`.
2. Revisar la extensa normalización de nombres españoles actualmente sin consolidar.
3. No descartar ni restaurar archivos automáticamente.
4. Corregir documentación desactualizada solo después de contrastarla con el código.

Discrepancias ya detectadas que requieren revisión:

- `README.md` describe algunos pasos de forma diferente al catálogo ejecutable de `backend/thesis/catalogo_pasos.py`.
- `docs/10_CONVENCIONES_NOMENCLATURA.md` todavía afirma que el frontend no realiza llamadas HTTP, aunque P01 ya está conectado.
- `docs/09_HANDOFF_IMPLEMENTACION_FRONTEND.md` describe P01 como trabajo futuro, aunque ya fue implementado.

Este hito no debe alterar lógica funcional.

### Hito 1 — Espacio de trabajo genérico para P02–P05

Objetivo: completar el capítulo 1 sin crear una pantalla manual independiente por cada paso.

Trabajo esperado:

1. Derivar tipos TypeScript desde el OpenAPI o establecer un proceso reproducible de generación.
2. Crear componentes genéricos para campos comunes del `esquema_salida`.
3. Mostrar P01–P05 desde el catálogo real.
4. Respetar `dependencias`, `estado` y `acciones_permitidas`.
5. Hidratar cada formulario con `datos_salida` y `contenido_md` persistidos.
6. Guardar con UUID y versión optimista.
7. Recargar el proyecto después de cada guardado.
8. Mostrar validaciones públicas del backend sin reinterpretarlas ni ocultarlas.

No conectar todavía P06–P12 en este hito.

### Hito 2 — Ciclo completo de revisión del capítulo 1

Objetivo: permitir que un tesista complete P01–P05 y envíe el capítulo 1 al asesor.

Trabajo esperado:

1. Consultar el estado real del capítulo 1.
2. Enviar el capítulo únicamente cuando los pasos requeridos estén completos.
3. Mostrar la revisión enviada e inmutable.
4. Bloquear acciones no permitidas según el backend.
5. Mostrar observaciones y estado de revisión.
6. Permitir reanudar edición cuando el backend lo habilite.

### Hito 3 — Conectar P06–P12

Objetivo: completar en el frontend los capítulos 2 y 3 ya soportados por el backend.

Trabajo esperado:

1. Reutilizar el espacio de trabajo genérico.
2. Renderizar P06–P12 desde el catálogo.
3. Respetar los contratos específicos de preguntas, objetivos, hipótesis, variables y matrices.
4. Visualizar la matriz de consistencia materializada.
5. Visualizar la matriz de operacionalización materializada.
6. Verificar el flujo completo de dependencias hasta P12.

### Hito 4 — Panel y revisión del asesor

Objetivo: conectar las capacidades de asesor ya existentes en el backend.

Trabajo esperado:

1. Panel de proyectos asignados.
2. Apertura de capítulos enviados.
3. Comentarios anclados a revisiones inmutables.
4. Listado y resolución de comentarios.
5. Aprobación o solicitud de cambios.
6. Estados visibles de carga, vacío, error y éxito.

No permitir que el asesor comente contenido que todavía sea un borrador editable.

### Hito 5 — Investigación, fuentes y exportación

Objetivo: exponer capacidades backend existentes sin exagerar su nivel de verificación.

Trabajo esperado:

1. Exploración de la idea.
2. Búsqueda en Semantic Scholar.
3. Búsqueda de antecedentes peruanos.
4. Filtros geográficos reales.
5. Etiquetas claras para `SOLO_METADATOS` y texto completo no inspeccionado.
6. Descarga del borrador DOCX.
7. Manejo visible de indisponibilidad de proveedores externos.

Nunca presentar metadatos o resúmenes como evidencia de lectura física completa.

### Hito 6 — Autenticación y experiencia de producto

Objetivo: dejar de depender visualmente del acceso al administrador de Django.

Antes de implementar, definir contratos backend reales para las funciones necesarias.

Posibles capacidades:

- Inicio de sesión propio.
- Cierre de sesión.
- Recuperación de acceso, solo si se aprueba y existe soporte backend.
- Gestión básica de cuenta.
- Gestión adicional de proyectos, solo cuando existan endpoints públicos para ello.

No simular registro, archivado, edición de proyecto ni recuperación de contraseña únicamente en el navegador.

### Hito 7 — Calidad frontend y preparación operativa

Objetivo: convertir los recorridos conectados en una aplicación mantenible.

Trabajo esperado:

1. Pruebas de componentes y recorridos reales en navegador.
2. Casos de sesión expirada, CSRF, vacío, validación y conflicto de versión.
3. Accesibilidad de teclado, etiquetas, foco y mensajes de estado.
4. Diseño adaptable para resoluciones menores.
5. Cliente OpenAPI reproducible.
6. Configuración documentada de desarrollo y producción con mismo origen o proxy común.
7. Integración continua que ejecute pruebas frontend y puertas backend.

## 7. Trabajo futuro fuera del alcance actual

No implementar hasta que el backend proporcione contratos comprobados:

- Chat web conectado a un agente.
- P13–P32 y capítulos 4–7.
- Ingesta y lectura física de PDF desde la aplicación.
- OCR.
- GROBID.
- Evidencias enlazadas a páginas físicas.
- Colaboración en tiempo real.
- WebSockets.
- Orquestación multiagente.

El panel de chat debe permanecer deshabilitado como “Próximamente”.

## 8. Pruebas mínimas por cada hito frontend

Cada hito debe comprobar, según corresponda:

1. Estado de carga.
2. Estado sin datos.
3. Estado de error con `codigo`, `mensaje` y `detalle`.
4. Sesión no autenticada.
5. Creación o apertura del recurso real.
6. Guardado con UUID válido.
7. Uso de la última `version_estado`.
8. Recarga desde PostgreSQL.
9. Persistencia de `contenido_md` y `datos_salida`.
10. Manejo de `CONFLICTO_VERSION` sin sobrescritura.
11. Ausencia de rutas, campos o estados públicos ingleses.
12. Ausencia de datos ficticios y mocks en producción.

## 9. Puerta obligatoria de entrega

No declarar un hito terminado por inspección visual.

Desde `../TesisMCP_Frontend/`, ejecutar los scripts definidos en `package.json`, incluyendo como mínimo:

```bash
pnpm pruebas
pnpm analizar
pnpm compilar
```

Desde `V1/`:

```bash
python3 scripts/verify_project.py
```

Desde la raíz `../`:

```bash
python3 scripts/verify_project.py
```

Todos los comandos deben terminar con código de salida 0. La entrega debe informar comandos, duración, código de salida, archivos modificados y decisiones de diseño.

El veredicto obligatorio es:

```text
[APROBADO_CON_EVIDENCIA / EXIT_CODE_0]
```

## 10. Instrucción lista para copiar a otro agente

```text
Continúa TesisMCP usando como relevo V1/docs/11_PLAN_CONTINUIDAD_PROYECTO.md.

Antes de modificar código, lee completamente todos los archivos indicados en su sección “Lectura obligatoria”. Inspecciona el estado real de V1/ y TesisMCP_Frontend/ y preserva todos los cambios preexistentes.

Implementa únicamente el siguiente hito no completado del plan. No agregues datos ficticios, mocks de producción, rutas inventadas ni capacidades futuras. Todo identificador controlado por TesisMCP debe estar en español. No modifiques migraciones ni datos persistidos salvo bloqueo demostrado y autorizado.

Ejecuta las pruebas focalizadas, el análisis y la compilación del frontend, la puerta de V1 y la puerta global. Entrega solo si todas terminan con código 0 y reporta [APROBADO_CON_EVIDENCIA / EXIT_CODE_0].
```

