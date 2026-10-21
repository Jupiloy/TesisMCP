# Guía técnica del frontend de TesisMCP

Esta carpeta explica el código que existe actualmente en `TesisMCP_Frontend/`. No describe pantallas futuras como si estuvieran implementadas ni sustituye los contratos del backend.

## Orden recomendado de lectura

1. [Arquitectura y recorrido de datos](01_ARQUITECTURA_Y_FLUJO.md)
2. [Arranque, configuración y herramientas](02_ARRANQUE_CONFIGURACION_Y_HERRAMIENTAS.md)
3. [Cliente HTTP, contratos y seguridad](03_CLIENTE_HTTP_CONTRATOS_Y_SEGURIDAD.md)
4. [Estado, navegación y persistencia](04_ESTADO_NAVEGACION_Y_PERSISTENCIA.md)
5. [Componentes y formularios metodológicos](05_COMPONENTES_Y_FORMULARIOS.md)
6. [Diseño visual y estilos](06_DISENO_VISUAL_Y_ESTILOS.md)
7. [Pruebas, diagnóstico y verificación](07_PRUEBAS_DIAGNOSTICO_Y_VERIFICACION.md)
8. [Mapa completo de archivos](08_MAPA_DE_ARCHIVOS.md)

## Alcance comprobado

La aplicación activa monta el recorrido metodológico P01–P12, consume la API real de Django, utiliza la sesión por cookie, crea y abre proyectos, guarda pasos con control de versión e idempotencia y vuelve a consultar el proyecto tras cada guardado exitoso. La disponibilidad de cada paso la decide el backend.

El panel principal, la biblioteca, la revisión, la exportación, el formato enriquecido y el chat aparecen deshabilitados y rotulados como «Próximamente». No existe una conexión a un agente desde este frontend.

## Regla para mantener esta guía

Cuando se agregue, elimine o cambie de responsabilidad un archivo de `src/`, `tests/` o la configuración raíz, debe actualizarse [el mapa de archivos](08_MAPA_DE_ARCHIVOS.md) y la guía temática correspondiente. Los nombres controlados por TesisMCP se escriben en español; los nombres impuestos por React, Vite, TypeScript o la Web API conservan su forma técnica.
