# Componentes y formularios metodológicos

## Composición del espacio de trabajo

`EspacioTrabajoPaso.tsx` crea el editor de tres paneles. La izquierda contiene la estructura metodológica; el centro contiene cabecera, avisos, editor narrativo y formulario; la derecha muestra control de versión y el asistente deshabilitado. El componente selecciona el formulario P01–P12 con un `switch` sobre `codigoPaso`.

Componentes auxiliares:

- `AvisosEstado`: muestra error, conflicto o éxito; el conflicto ofrece recarga.
- `CabeceraPaso`: presenta capítulo, código, nombre, objetivo, dependencias y estado real.
- `EditorContenidoNarrativo`: edita el Markdown común a todos los pasos.
- `PanelAsistenteProximamente`: mantiene chat y envío deshabilitados.
- `NavegacionMetodologia`: árbol capitular, avance y estados.

## Formularios P01–P12

| Paso | Datos estructurados principales |
|---|---|
| P01 | Temas propuestos, pros, contras, viabilidad y tema preseleccionado. |
| P02 | Matriz comparativa, criterios, puntaje total y tema ganador. |
| P03 | ODS principal, meta, argumento de alineación y línea UTP. |
| P04 | Título oficial, variables, unidad de análisis, lugar y periodo. |
| P05 | Introducción, número de párrafos y palabras; puede sincronizar el texto narrativo. |
| P06 | Problema central, causas, efectos y preguntas. |
| P07 | Justificaciones teórica, práctica, metodológica y social, más resumen. |
| P08 | Brecha, aporte y estado fijo `EVIDENCIA_PENDIENTE`. |
| P09 | Objetivo general y objetivos específicos con verbos permitidos de Bloom. |
| P10 | Pregunta general y preguntas específicas con signos de interrogación. |
| P11 | Tipo de investigación, hipótesis y variables independiente/dependiente. |
| P12 | Matriz de operacionalización, dimensiones, indicadores y escala. |

Cada formulario exporta una función o constante `salidaPxxInicial`. Estas estructuras se usan cuando el backend todavía no devolvió datos para el paso.

## Componentes comunes

- `CampoTextoConContador`: entrada o área de texto con contador y señales de validación.
- `ListaDinamicaItems`: agrega, actualiza y elimina elementos dentro de mínimos y máximos configurables.
- `BadgeEstadoPaso`: insignia reutilizable para `COMPLETADO`, `DISPONIBLE` y `BLOQUEADO`; actualmente no participa en la pantalla montada.
- `ErrorBoundary`: captura errores de renderizado y evita una pantalla completamente blanca.

## Validación

Los formularios implementan restricciones de longitud, cantidad, enumeraciones y formato para orientar al usuario. Varias reglas están también cubiertas por las pruebas de contrato. Aun así, la aceptación definitiva de `datos_salida` es responsabilidad del esquema del backend.

## Controles deliberadamente inactivos

La barra conserva botones de deshacer, rehacer, negrita, cursiva, lista y estilo visual, pero están deshabilitados. No existe edición enriquecida. El asistente, comentarios, exportación y módulos laterales futuros también permanecen inactivos.
