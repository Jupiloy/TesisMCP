# Estado, navegación y persistencia

## Estado principal

`RecorridoCapitulos.tsx` concentra el estado de esta etapa del proyecto:

- sesión, catálogo, lista de proyectos y proyecto abierto;
- paso activo y capítulos expandidos;
- contenido narrativo y datos estructurados;
- carga inicial, apertura, creación y guardado;
- ausencia de sesión, error, conflicto y confirmación;
- campos temporales del formulario de nuevo proyecto.

No se utiliza una biblioteca global de estado. Para el alcance actual, el estado se mantiene con hooks de React y se distribuye por propiedades.

## Hidratación de formularios

`hidratarFormularioPaso` busca el paso dentro del proyecto. Si hay `datos_salida` no vacíos, los usa; de lo contrario carga la estructura inicial del formulario correspondiente. También copia `contenido_md` al editor narrativo.

Este proceso se usa al abrir proyecto, cambiar de paso y recargar después de guardar. Así se evita confundir el borrador de un paso con otro.

## Navegación metodológica

`NavegacionMetodologia.tsx` recibe capítulos, catálogo y estado real. Calcula el porcentaje mostrado a partir del número de pasos `COMPLETADO`, representa los estados con iconos y permite plegar cada capítulo.

Un paso `BLOQUEADO` está deshabilitado. Un paso `DISPONIBLE` o `COMPLETADO` puede abrirse. El componente no altera dependencias.

## Creación y apertura de proyectos

Si la lista está vacía, se solicitan nombre y título provisional. Tras el `POST`, se vuelve a listar, se abre el estado devuelto y se hidrata P01. El selector lateral permite abrir otro proyecto mediante su identificador.

## Persistencia comprobable desde la interfaz

El mensaje exitoso solo se asigna después del `GET` posterior al guardado. Esa secuencia demuestra que la pantalla recibió de nuevo los datos desde el backend; la prueba automatizada integral del almacenamiento corresponde a Django y PostgreSQL, no a las pruebas unitarias Node.

## Estados visibles

- carga inicial a pantalla completa;
- sesión ausente;
- lista sin proyectos y creación;
- error de conexión y reintento;
- proyecto en apertura;
- paso bloqueado y dependencias;
- guardado en curso;
- confirmación de persistencia;
- conflicto de versión y recarga.
