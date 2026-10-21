# TesisMCP — guía para revisión

Este proyecto contiene un prototipo funcional de escritorio para una aplicación de acompañamiento de tesis.

## Tecnologías

- React 19
- TypeScript
- Vite
- Tailwind CSS 4
- CSS global en `src/index.css`

## Archivos principales

- `src/App.tsx`: componentes, contenido e interacciones de las cinco pantallas.
- `src/index.css`: sistema visual, tokens y estilos de toda la aplicación.
- `src/main.tsx`: punto de entrada de React.
- `package.json`: scripts y dependencias.

## Pantallas

La navegación lateral permite abrir:

1. Panel principal del tesista.
2. Editor metodológico de tres paneles.
3. Biblioteca científica.
4. Dashboard del asesor.
5. Revisión del asesor.

El editor metodológico es la pantalla inicial y la vista más detallada.

## Ejecución local

Requiere Node.js y pnpm.

```bash
pnpm install
pnpm dev
```

Para crear una compilación de producción:

```bash
pnpm build
```

## Puntos sugeridos para analizar

- Arquitectura y reutilización de componentes.
- Accesibilidad y navegación mediante teclado.
- Adaptación a resoluciones menores.
- Separación futura de `App.tsx` en módulos.
- Conexión con un backend, almacenamiento de documentos y autenticación.
- Integración real de fuentes PDF y asistente metodológico.
