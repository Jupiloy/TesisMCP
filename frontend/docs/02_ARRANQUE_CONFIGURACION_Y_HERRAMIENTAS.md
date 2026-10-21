# Arranque, configuración y herramientas

## Tecnologías declaradas

El `package.json` declara React 19, React DOM 19, TypeScript, Vite 8, Tailwind CSS 4, `lucide-react`, `clsx` y `tailwind-merge`. Las herramientas de desarrollo son `oxlint`, `oxfmt`, el compilador TypeScript y el corredor de pruebas incorporado de Node.

## Archivos de arranque

- `index.html`: documento base y contenedor `root`.
- `src/main.tsx`: crea la raíz React e importa `src/index.css`.
- `src/App.tsx`: monta `RecorridoCapitulos` dentro de `ErrorBoundary`.
- `src/vite-env.d.ts`: tipos ambientales proporcionados por Vite.

## Configuración de TypeScript

`tsconfig.json` activa modo estricto, resolución para empaquetadores, JSX de React y ausencia de emisión. El alias `@/*` apunta a `src/*`. El proyecto se analiza con `pnpm analizar`, que ejecuta `tsc --noEmit`.

## Configuración de Vite

`vite.config.ts`:

- integra React y Tailwind;
- aplica los metadatos de `.figma/make/site.json`;
- conserva complementos de previsualización de Figma Make;
- expone el servidor de desarrollo en el puerto configurado o 8443;
- redirige `/api`, `/admin` y `/salud` a Django en `127.0.0.1:8000`;
- genera mapas de fuentes integrados en modo de desarrollo;
- usa `FIGMA_PUBLIC_URL` cuando se proporciona una base de despliegue.

El proxy evita codificar un origen alternativo en el cliente: las llamadas siguen siendo del mismo origen desde la perspectiva del navegador.

## Comandos disponibles

| Comando | Propósito |
|---|---|
| `pnpm dev` | Servidor de desarrollo Vite. |
| `pnpm pruebas` | Pruebas `node:test` de `tests/*.test.mjs`. |
| `pnpm analizar` | Verificación estática de TypeScript. |
| `pnpm lint` | Análisis de `src/` con Oxlint. |
| `pnpm compilar` | Compilación de producción con Vite. |
| `pnpm preview` | Previsualización del resultado compilado. |
| `pnpm format` | Formato mediante Oxfmt. |

## Configuración heredada de Figma

La carpeta `.figma/` y varios complementos de `vite.config.ts` proceden del proyecto generado/importado con Figma Make. Son parte de la infraestructura visual y de previsualización, pero no contienen la lógica de negocio metodológica.
