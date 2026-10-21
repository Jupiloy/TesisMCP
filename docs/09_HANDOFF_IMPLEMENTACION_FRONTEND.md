# 09. Relevo para la Implementación Frontend–Backend

## 1. Objetivo del siguiente chat

Continuar TesisMCP conectando progresivamente el prototipo React de `TesisMCP_Frontend/` con el avance evolutivo del backend `V1/`. El primer hito es un recorrido vertical P01 real: sesión, proyecto, catálogo, edición, validación, persistencia PostgreSQL y recarga.

No se debe rediseñar desde cero la interfaz ni importar indiscriminadamente todo el backend de la versión completa.

---

## 2. Lectura obligatoria antes de modificar código

El nuevo chat debe leer, en este orden:

1. `AGENTS.md` de la raíz del proyecto.
2. `GUIA_AGENTE.md` de la raíz del proyecto.
3. `V1/README.md`.
4. `V1/docs/08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md`.
5. Este documento.
6. `TesisMCP_Frontend/AGENTS.md`.
7. `TesisMCP_Frontend/CHATGPT_REVIEW.md`.
8. `TesisMCP_Frontend/src/App.tsx` y `src/index.css`.
9. `V1/backend/config/api.py`.
10. `V1/backend/thesis/api/proyectos.py` y los servicios invocados por sus rutas.

Los archivos reales prevalecen sobre este resumen si existe cualquier discrepancia.

---

## 3. Límites de alcance

### Dentro del primer hito

- Conservar el sistema visual generado en Figma.
- Configurar comunicación del frontend con Django.
- Implementar sesión o identificar el mecanismo mínimo de autenticación del recorrido.
- Listar proyectos reales del usuario.
- Exponer y consumir el catálogo P01 a P12.
- Abrir un proyecto.
- Mostrar el paso P01 y sus prerrequisitos.
- Guardar P01 usando el contrato real.
- Recargar y comprobar persistencia.
- Mostrar errores de validación y conflictos de versión.

### Fuera del primer hito

- P02 a P32.
- Carga y extracción de PDFs.
- OCR, GROBID o pgvector.
- Evidencia por página física.
- Chat web con un proveedor de IA.
- Agentes autónomos u OpenAgents.
- Editor equivalente a Microsoft Word.
- Colaboración en tiempo real.
- Microservicios.

---

## 4. Estado técnico comprobado

### Backend `V1/`

- Implementa P01 a P12.
- Usa Django Ninja y autenticación de sesión mediante `django_auth`.
- Dispone de creación y consulta individual de proyectos, pero no de listado de proyectos para el tesista.
- El catálogo existe en `backend/thesis/catalogo_pasos.py`, pero no está expuesto como recurso HTTP.
- `guardar_paso_servicio` exige `contenido_md`, `datos_salida`, `version_esperada` y `clave_idempotencia`.
- Los pasos se desbloquean secuencialmente.
- La revisión del asesor ya dispone de endpoints y servicios.
- El MCP funciona por `stdio`; no existe un endpoint de chat web.

### Frontend `TesisMCP_Frontend/`

- Usa React 19, TypeScript, Vite y Tailwind CSS 4.
- Presenta cinco pantallas y comienza en el editor metodológico.
- `src/App.tsx` concentra 1312 líneas.
- No contiene llamadas `fetch` ni cliente HTTP.
- Los datos son ejemplos locales.
- Muestra capítulos 1 a 7 y 32 pasos, por lo que debe adaptarse al catálogo real.
- Simula PDFs y fragmentos físicos no disponibles en `V1`.
- `node_modules` no estaba instalado durante la revisión inicial. La primera ejecución de `pnpm build` no alcanzó la compilación porque el entorno restringido no pudo crear el almacén de pnpm en el directorio personal; no se diagnosticó un error de TypeScript a partir de ese intento.

### Estado previo que debe preservarse

Antes de crear estos documentos ya existía una modificación local en:

```text
V1/mcp_server/__init__.py
```

Debe tratarse como trabajo preexistente del usuario y no revertirse ni incluirse incidentalmente en cambios no relacionados.

---

## 5. Primer contrato vertical

El recorrido esperado es:

```text
Usuario autenticado
      ↓
GET proyectos propios
      ↓
Seleccionar proyecto
      ↓
GET estado + catálogo metodológico
      ↓
Abrir P01
      ↓
Completar contenido narrativo y datos estructurados
      ↓
PUT P01 con `version_esperada` y `clave_idempotencia`
      ↓
Persistencia PostgreSQL
      ↓
Recargar y observar P01 completado / P02 disponible
```

### Endpoints mínimos a evaluar

Los nombres definitivos deben conservar coherencia con la API existente:

```text
GET  /api/v1/sesion/actual
GET  /api/v1/metodologia/catalogo
GET  /api/v1/proyectos
POST /api/v1/proyectos
GET  /api/v1/proyectos/{id_proyecto}
PUT  /api/v1/proyectos/{id_proyecto}/pasos/P01
```

No se deben crear rutas duplicadas si la información ya puede incorporarse limpiamente en una respuesta existente.

---

## 6. Trabajo frontend del primer hito

1. Crear un cliente HTTP pequeño y tipado.
2. Configurar el proxy de desarrollo de Vite hacia Django.
3. Extraer el armazón general, navegación y editor de `App.tsx` sin una reescritura masiva.
4. Crear estados de carga, error, vacío y conflicto.
5. Sustituir los 32 pasos por el catálogo recibido.
6. Mostrar únicamente capítulos 1 a 3.
7. Crear el formulario P01 con los campos exactos de su contrato Pydantic.
8. Mantener separado `contenido_md` de `datos_salida`.
9. Generar una clave UUID de idempotencia por intento lógico de guardado.
10. Actualizar `version_estado` con la respuesta exitosa.

El primer cambio no debe intentar modularizar simultáneamente las cinco pantallas completas. Se extraerá solo lo necesario para el recorrido P01 y se repetirá el patrón en los siguientes hitos.

---

## 7. Reglas funcionales que no deben romperse

- Nunca omitir `version_esperada`.
- Nunca reutilizar una `clave_idempotencia` para contenido diferente.
- No habilitar un paso cuyo prerrequisito no esté completado.
- No traducir silenciosamente un error `CONFLICTO_VERSION` a guardado exitoso.
- No comentar el borrador vivo: el asesor comenta una revisión enviada e inmutable.
- No etiquetar una fuente como texto completo verificado si solo existen metadatos.
- No usar datos ilustrativos del prototipo como evidencia académica.
- No declarar que el chat del panel derecho está conectado mientras MCP continúe solo por `stdio`.

---

## 8. Criterios de aceptación del primer hito

El hito solo puede considerarse alcanzado si:

1. El frontend compila sin errores.
2. Django pasa `manage.py check`.
3. No existen migraciones pendientes inesperadas.
4. La suite actual continúa en verde.
5. Las pruebas nuevas cubren listado/catálogo y guardado P01 según los cambios realizados.
6. Un usuario puede abrir un proyecto real y completar P01 desde la interfaz.
7. La información permanece después de recargar.
8. P02 cambia de bloqueado a disponible conforme al estado real.
9. Una `version_esperada` obsoleta muestra un conflicto comprensible.
10. No se incorporan archivos temporales, cachés ni datos simulados residuales en servicios de producción.

---

## 9. Verificación obligatoria

Desde `V1/`:

```bash
python3 scripts/verify_project.py
```

Desde `TesisMCP_Frontend/`, después de instalar las dependencias de forma controlada:

```bash
pnpm build
```

Si se agregan pruebas frontend, deberán ejecutarse también mediante el script definido en `package.json`. La entrega debe reportar comandos, tiempos, códigos de salida y el veredicto de la puerta DoD.

---

## 10. Primera instrucción sugerida para el nuevo chat

> Lee `AGENTS.md`, `GUIA_AGENTE.md`, `V1/docs/08_ARQUITECTURA_EVOLUTIVA_FRONTEND_BACKEND.md` y `V1/docs/09_HANDOFF_IMPLEMENTACION_FRONTEND.md`. Después inspecciona `V1/` y `TesisMCP_Frontend/`. Implementa únicamente el primer recorrido vertical P01 descrito en el relevo, preservando cambios preexistentes y ejecutando la puerta de verificación completa antes de entregar.

