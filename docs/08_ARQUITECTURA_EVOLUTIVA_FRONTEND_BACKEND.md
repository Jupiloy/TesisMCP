# 08. Arquitectura Evolutiva Frontend–Backend de TesisMCP

## 1. Propósito y decisión principal

Este documento fija la arquitectura acordada para conectar el prototipo visual ubicado en `TesisMCP_Frontend/` con el avance evolutivo del backend ubicado en `V1/`, sin convertir este avance en código desechable ni crear dos productos divergentes.

La decisión principal es:

> **TesisMCP será un único producto modular que incorpora capacidades progresivamente. `V1` es una fotografía temporal de las capacidades actualmente disponibles, no una capacidad, edición comercial ni aplicación separada.**

Por tanto, no se implementarán condiciones de negocio basadas en etiquetas como `V1` o `ADVANCED`. El frontend debe representar los recursos y acciones que el backend expone realmente.

---

## 2. Estado real de los dos componentes

### 2.1. Avance evolutivo del backend `V1/`

El backend actual implementa:

- Django, Django Ninja y PostgreSQL.
- Usuarios, proyectos y participantes.
- Capítulos 1 a 3 y pasos metodológicos P01 a P12.
- Contratos Pydantic estrictos para los doce pasos.
- Control de concurrencia optimista mediante el campo ORM histórico `lock_version` y el contrato público `version_esperada`.
- Revisiones inmutables, comentarios del asesor y decisiones de aprobación o solicitud de cambios.
- Búsqueda por metadatos en OpenAlex, Semantic Scholar y ALICIA/Perú.
- Exportación de borrador DOCX.
- Servidor MCP por transporte `stdio`.

No implementa todavía:

- Pasos P13 a P32.
- Carga, extracción o visualización real de PDF.
- Evidencias localizadas por página física.
- Chat web con un modelo de lenguaje.
- Editor web persistente.
- Frontend propio del tesista.

### 2.2. Prototipo `TesisMCP_Frontend/`

El prototipo usa React 19, TypeScript, Vite y Tailwind CSS 4. Contiene cinco pantallas:

1. Panel principal del tesista.
2. Editor metodológico de tres paneles.
3. Biblioteca científica.
4. Dashboard del asesor.
5. Revisión del asesor.

La interfaz reproduce adecuadamente la visión de producto NotebookLM + Word/Docs + asesor/IA, pero actualmente:

- Los datos están declarados dentro de `src/App.tsx`.
- No existen llamadas HTTP al backend.
- La hoja central es una representación visual, no un editor de texto persistente.
- Los proyectos, estudiantes, fuentes, comentarios y métricas son ejemplos de interfaz.
- Presenta 32 pasos, capítulos 1 a 7, PDFs y evidencia física que no pertenecen al alcance funcional actual de `V1`.

Los ejemplos del prototipo no constituyen evidencia académica ni datos reales del sistema.

---

## 3. Arquitectura objetivo

```text
┌──────────────────────────────────────────────────────┐
│ React + TypeScript + Vite                            │
│                                                      │
│ Proyecto · Metodología · Fuentes · Revisión · DOCX  │
└──────────────────────────┬───────────────────────────┘
                           │ /api/v1
                           ▼
┌──────────────────────────────────────────────────────┐
│ Django Ninja                                         │
│                                                      │
│ API → servicios de dominio → ORM                    │
└──────────────────────────┬───────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────┐
│ PostgreSQL                                           │
│                                                      │
│ Estado metodológico, revisiones e historial          │
└──────────────────────────────────────────────────────┘
```

Se mantendrá un **monolito modular Django**. No se introducirán microservicios, WebSockets, colaboración en tiempo real ni orquestadores multiagente mientras el alcance no los requiera.

Durante el desarrollo, Vite debe redirigir `/api`, `/admin` y `/salud` hacia Django. En producción se debe conservar un mismo origen público o un proxy común para evitar complejidad innecesaria con sesiones, CSRF y CORS.

---

## 4. Organización objetivo del frontend

`src/App.tsx` debe dejar de concentrar pantallas, contenido, estado y datos simulados. La separación objetivo es:

```text
src/
├── app/
│   ├── App.tsx
│   ├── router.tsx
│   └── providers.tsx
├── features/
│   ├── auth/
│   ├── projects/
│   ├── methodology/
│   ├── editor/
│   ├── sources/
│   ├── reviews/
│   ├── advisor/
│   └── export/
├── components/
│   ├── layout/
│   ├── feedback/
│   └── ui/
├── lib/
│   ├── api/
│   ├── errors/
│   └── formatting/
└── types/
    └── api.generated.ts
```

No es necesario crear toda la estructura en un solo cambio. Cada carpeta debe aparecer cuando exista una funcionalidad real que alojar.

### Estado de la aplicación

- **Estado del servidor:** proyectos, pasos, revisiones y fuentes. Puede administrarse con TanStack Query cuando comience la integración HTTP.
- **Estado de interfaz:** pestañas, paneles, modal activo y selección visual. Puede continuar con estado local de React.
- **Estado de edición:** contenido y formulario aún no guardados. Debe permanecer local hasta una acción explícita de guardado.

No se incorporará Redux mientras no exista una necesidad demostrada.

---

## 5. Catálogo metodológico dirigido por el backend

El frontend no debe contener una pantalla independiente codificada manualmente para cada paso. El catálogo del backend será la fuente de verdad para:

- Código y capítulo.
- Nombre y propósito.
- Prerrequisitos.
- Estado del paso.
- Campos estructurados.
- Acciones permitidas.
- Versión del estado.

La respuesta conceptual de un paso será semejante a:

```json
{
  "codigo": "P04",
  "capitulo": 1,
  "nombre": "Delimitación final y título",
  "dependencias": ["P03"],
  "estado": "DISPONIBLE",
  "acciones_permitidas": ["GUARDAR"],
  "version_estado": 4
}
```

El frontend usará un espacio de trabajo genérico:

```text
StepWorkspace
├── StepInstructions
├── DynamicStepForm
├── NarrativeEditor
├── ValidationSummary
└── StepActions
```

Los pasos con una estructura visual especial, como la matriz de consistencia o la matriz de operacionalización, podrán registrar un renderizador especializado. Los demás pasos reutilizarán el formulario genérico.

Cuando el backend incorpore P13, el frontend no debe requerir una condición llamada `isAdvanced`; debe recibir el nuevo paso a través del catálogo.

---

## 6. Capacidades y evolución

En la primera integración no se construirá un sistema complejo de *feature flags*. Se aplicará esta regla:

> **La existencia real del recurso o acción en el backend determina si la interfaz puede mostrarlo como funcional.**

Ejemplos:

- Si el catálogo devuelve P01 a P12, se muestran doce pasos.
- Si no existe carga de PDF, no se presenta como una acción funcional.
- Si una fuente solo tiene metadatos, se etiqueta `Solo metadatos`.
- Cuando exista evidencia física, se habilitará el visor de fragmentos.

Un endpoint `/api/v1/capabilities` podrá añadirse cuando sea necesario activar funciones experimentales, desplegar módulos gradualmente o ofrecer configuraciones institucionales diferentes. No debe almacenar una etiqueta global `V1` o `ADVANCED`; debe describir hechos concretos.

---

## 7. Contrato HTTP y tipado

La API continuará versionada bajo `/api/v1/`. La dirección objetivo es:

```text
/api/v1/
├── sesion/actual
├── metodologia/catalogo
├── proyectos
│   └── {id_proyecto}
│       ├── state
│       ├── pasos/{codigo_paso}
│       ├── capitulos/{numero_capitulo}
│       ├── fuentes
│       ├── revisiones
│       └── exportar
└── asesor
    ├── panel
    └── asignaciones
```

No todos estos endpoints existen todavía. Deben agregarse únicamente conforme avance cada recorrido vertical.

Los tipos TypeScript deben derivarse del OpenAPI de Django Ninja para evitar duplicar manualmente enums, estados y estructuras. Las etiquetas visuales en español se resolverán en el frontend sin alterar los valores estables del dominio.

---

## 8. Editor y datos metodológicos

La hoja central debe parecerse a Word sin intentar reconstruir Microsoft Word. La decisión técnica prevista es emplear TipTap cuando comience la edición real.

Se deben separar dos representaciones:

```text
Contenido narrativo de la revisión → contenido_md
Datos metodológicos validados      → datos_salida
```

El usuario puede trabajar en una interfaz familiar, pero los campos que alimentan título, variables, objetivos, hipótesis o matrices deben conservar su estructura validable.

El frontend debe enviar `version_esperada` y `clave_idempotencia` y manejar explícitamente `409 CONFLICTO_VERSION`. Nunca debe sobrescribir silenciosamente un cambio concurrente.

---

## 9. Revisiones y comentarios

Los comentarios del asesor se anclan a una revisión enviada e inmutable, no al borrador vivo del estudiante:

```text
Borrador editable
      ↓ enviar capítulo
Revisión inmutable
      ↓
Comentarios anclados
      ↓
Solicitud de cambios o aprobación
```

Esta regla preserva la validez de `inicio_caracter`, `fin_caracter` y `texto_seleccionado`. Una nueva edición del estudiante genera una revisión posterior; no altera el texto histórico comentado.

---

## 10. Evolución de fuentes

La interfaz debe representar niveles de verificación, no un estado binario ficticio:

```text
Solo metadatos
Documento registrado
Texto completo extraído
Fragmento localizado
Página física comprobada
```

En el alcance actual solo están disponibles búsquedas por metadatos. La carga de PDF, OCR, fragmentos y evidencia por página se incorporarán después reutilizando la misma sección de fuentes.

---

## 11. Asistente y MCP

El panel derecho no debe acoplarse a OpenAI, Claude ni otro proveedor. En el alcance actual puede mostrar:

- Validaciones deterministas.
- Prompts metodológicos disponibles.
- Observaciones del asesor.
- Actividad proveniente de un cliente MCP externo.

El chat web se añadirá cuando exista un contrato backend específico para ejecuciones del asistente. El transporte MCP actual es `stdio`; no debe presentarse como chat web conectado hasta implementar esa capacidad.

---

## 12. Secuencia de crecimiento acordada

1. Base técnica del frontend y cliente HTTP.
2. Sesión y lista real de proyectos.
3. Recorrido vertical P01 con persistencia PostgreSQL.
4. Renderizador reutilizable y pasos P02 a P12.
5. Envío y revisión de capítulos 1 a 3.
6. Dashboard del asesor y comentarios anclados.
7. Búsqueda científica por metadatos.
8. Exportación DOCX desde la interfaz.
9. Carga y procesamiento documental.
10. Evidencia por fragmento y página física.
11. Incorporación progresiva de P13 a P32.

Cada punto debe entregar una funcionalidad verificable de extremo a extremo. No se completarán todas las pantallas con datos simulados antes de integrar el primer recorrido real.

