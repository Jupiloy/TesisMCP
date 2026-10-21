# Diseño visual y estilos

## Fuente de estilos

`src/index.css` es la hoja global. Importa Tailwind CSS y las familias Inter y Source Serif 4 desde Google Fonts. También define variables de color, superficies, sombras y tipografía.

## Estructura visual activa

La pantalla combina:

1. barra global azul oscuro con marca, navegación futura, selector de proyecto y perfil;
2. barra superior con ruta y versión;
3. título y barra de herramientas del documento;
4. panel izquierdo para capítulos y pasos;
5. hoja central desplazable para edición;
6. panel derecho de control de guardado y asistente futuro.

La sección final de la hoja, identificada como recuperación del editor de tres paneles, ajusta la estructura activa para acercarla al prototipo de Figma sin habilitar funciones inexistentes.

## Convenciones de clase

La interfaz principal usa clases semánticas en español como `barra-metodologia`, `pagina-p01`, `tarjeta-formulario` y `aviso-conflicto`. Algunos componentes comunes utilizan utilidades Tailwind y la función `cn` de `src/lib/utils.ts` para combinar clases y resolver colisiones.

## Adaptación a anchuras

Las reglas `@media` reducen columnas o apilan regiones cuando disminuye el ancho. La hoja central conserva un mínimo para formularios complejos, especialmente la matriz P12, por lo que en pantallas estrechas se prioriza mantener campos utilizables frente a replicar exactamente el escritorio.

## Código visual heredado

La hoja conserva estilos de pantallas y etapas anteriores del prototipo. No toda clase declarada corresponde a un nodo montado por `App.tsx`. Antes de eliminar CSS aparentemente sin uso, debe comprobarse si pertenece a una pantalla histórica que el equipo desea conservar.

## Accesibilidad presente y límites

Existen etiquetas, estados `disabled`, `aria-current`, `aria-expanded`, regiones de alerta y textos alternativos para iconos decorativos. La configuración de Figma puede agregar un enlace de salto. Esta guía no afirma conformidad WCAG completa: no existe en el repositorio una auditoría automatizada integral de accesibilidad.
