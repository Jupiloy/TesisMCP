# Mapa completo de archivos

## Raíz y configuración

| Archivo | Responsabilidad |
|---|---|
| `AGENTS.md` | Reglas locales obligatorias para agentes. |
| `CHATGPT_REVIEW.md` | Revisión y contexto heredado del prototipo. |
| `CLAUDE.md` | Instrucciones heredadas para otro asistente. |
| `index.html` | Documento HTML de entrada. |
| `package.json` | Dependencias y comandos. |
| `pnpm-lock.yaml` | Resolución reproducible de dependencias. |
| `tsconfig.json` | Reglas de TypeScript. |
| `vite.config.ts` | Construcción, Figma Make y proxy a Django. |
| `.figma/make/site.json` | Metadatos del sitio usados por Vite. |
| `.gitignore`, `.gitattributes`, `.mise.toml` | Higiene Git y entorno de herramientas. |
| `public/favicon.svg` | Icono público. |

## Entrada y utilidades

| Archivo | Responsabilidad |
|---|---|
| `src/main.tsx` | Arranque de React y carga del CSS. |
| `src/App.tsx` | Composición raíz activa. |
| `src/index.css` | Sistema visual global y reglas adaptables. |
| `src/vite-env.d.ts` | Tipos de Vite. |
| `src/lib/utils.ts` | Combinación de clases mediante `cn`. |

## API

| Archivo | Responsabilidad |
|---|---|
| `src/lib/api/contrato.mjs` | Rutas y constructores puros de cargas y errores. |
| `src/lib/api/contrato.d.mts` | Declaraciones TypeScript del contrato JavaScript. |
| `src/lib/api/cliente.ts` | Tipos de dominio, sesión/CSRF y operaciones `fetch`. |

## Recorridos

| Archivo | Estado y responsabilidad |
|---|---|
| `src/features/metodologia/RecorridoCapitulos.tsx` | Activo: sesión, proyectos, P01–P12 y persistencia. |
| `src/features/metodologia/RecorridoCapitulo1.tsx` | Histórico: recorrido P01–P05, no montado. |
| `src/features/metodologia/RecorridoP01.tsx` | Histórico: primer recorrido P01, no montado. |

## Componentes metodológicos

| Archivo | Responsabilidad |
|---|---|
| `AvisosEstado.tsx` | Avisos de error, conflicto y éxito. |
| `CabeceraPaso.tsx` | Metadatos y estado del paso. |
| `EditorContenidoNarrativo.tsx` | Campo `contenido_md`. |
| `EspacioTrabajoPaso.tsx` | Editor de tres paneles y selección de formulario. |
| `NavegacionMetodologia.tsx` | Árbol de capítulos, avance y bloqueo. |
| `PanelAsistenteProximamente.tsx` | Panel de chat deshabilitado. |
| `FormularioP01.tsx` … `FormularioP12.tsx` | Edición de la salida estructurada de cada paso. |

## Componentes comunes

| Archivo | Responsabilidad |
|---|---|
| `BadgeEstadoPaso.tsx` | Insignia de estado reutilizable. |
| `CampoTextoConContador.tsx` | Texto con longitud y validación visual. |
| `ListaDinamicaItems.tsx` | Colecciones editables con límites. |
| `ErrorBoundary.tsx` | Recuperación ante errores de renderizado. |

## Pruebas

| Archivo | Cobertura declarada |
|---|---|
| `tests/cliente-api.test.mjs` | Contrato del cliente HTTP. |
| `tests/recorrido-capitulo1.test.mjs` | P01–P05. |
| `tests/recorrido-capitulo2.test.mjs` | P06–P08. |
| `tests/recorrido-capitulo3.test.mjs` | P09–P12. |

## Dónde realizar cada cambio

- Nueva operación HTTP: contrato, declaración y `cliente.ts`, seguida de pruebas.
- Nueva regla de datos de un paso: formulario, tipos del cliente, contrato real del backend y pruebas.
- Cambio de flujo global: `RecorridoCapitulos.tsx`.
- Cambio de composición del editor: `EspacioTrabajoPaso.tsx`.
- Cambio del árbol metodológico: `NavegacionMetodologia.tsx` y catálogo del backend si corresponde.
- Cambio visual: `index.css`, preservando estados deshabilitados y adaptabilidad.
- Nueva capacidad futura: no habilitarla hasta que exista un endpoint real y su verificación integral.
