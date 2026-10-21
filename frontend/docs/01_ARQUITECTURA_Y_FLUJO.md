# Arquitectura y recorrido de datos

## Capas actuales

```text
index.html
  └─ src/main.tsx
      └─ src/App.tsx
          └─ ErrorBoundary
              └─ RecorridoCapitulos
                  ├─ cliente HTTP y contrato público
                  ├─ NavegacionMetodologia
                  └─ EspacioTrabajoPaso
                      ├─ editor narrativo
                      ├─ formulario P01…P12
                      └─ panel de asistente deshabilitado
```

`main.tsx` crea la raíz de React, activa `StrictMode` e importa el CSS global. `App.tsx` envuelve la pantalla activa con un límite de errores. La única experiencia montada es `RecorridoCapitulos.tsx`.

## Flujo inicial

1. `RecorridoCapitulos` consulta la sesión.
2. Si la sesión es válida, solicita en paralelo el catálogo metodológico y la lista de proyectos.
3. Si existe al menos un proyecto, abre el primero con una consulta de detalle.
4. Si no existe ninguno, presenta el formulario de creación.
5. El estado recibido hidrata el contenido Markdown y los datos estructurados del paso activo.

La carga, la ausencia de sesión, el error de conexión, el estado vacío, la apertura de un proyecto y la confirmación de guardado tienen representaciones visibles distintas.

## Flujo de edición y guardado

El componente mantiene dos partes editables: `contenido`, correspondiente a `contenido_md`, y `datosSalida`, correspondiente a `datos_salida`. El formulario específico depende del código P01–P12.

Al guardar:

1. se bloquea el intento si el backend marcó el paso como `BLOQUEADO`;
2. se genera `clave_idempotencia` con `crypto.randomUUID()`;
3. se usa `proyecto.version_estado` como `version_esperada`;
4. se ejecuta el `PUT` del paso;
5. se vuelve a ejecutar el `GET` del proyecto;
6. se reemplaza el estado local por la respuesta recargada;
7. solo entonces se muestra la confirmación de persistencia.

Un `CONFLICTO_VERSION` se muestra por separado y ofrece recargar la versión actual. El frontend no sobrescribe silenciosamente un estado más reciente.

## Dependencias entre pasos

La interfaz no calcula qué paso debe desbloquearse. Lee `estado`, `dependencias` y `acciones_permitidas` del detalle del proyecto. La navegación deshabilita los pasos bloqueados y muestra las dependencias informadas por el backend.

## Código activo y código histórico

- `RecorridoCapitulos.tsx`: recorrido activo P01–P12, importado por `App.tsx`.
- `RecorridoCapitulo1.tsx`: implementación anterior limitada a P01–P05; no está montada.
- `RecorridoP01.tsx`: primer recorrido vertical aislado; no está montado.

Los dos archivos históricos permiten rastrear la evolución, pero no deben modificarse esperando un efecto visual en la aplicación actual.
