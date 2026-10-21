# Explicación de Código: `backend/thesis/services/materializadores_pasos/registro.py`

## 1. Propósito y ¿Qué hace?
Provee el registro y despachador polimórfico de materializadores relacionales. Permite asociar funciones materializadoras específicas a cada paso o conjunto de capítulos, desacoplando el servicio general de guardado de los detalles particulares de persistencia de cada capítulo.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Principio Abierto/Cerrado (OCP):** Facilita que cuando se incorporen los Capítulos 4 al 7 en fases posteriores, se puedan registrar nuevos materializadores sin alterar el código de `pasos.py`.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Mantiene el diccionario `MATERIALIZADORES: dict[str, Callable]`.
2. Asocia los pasos `P01` a `P12` con `materializar_paso_capitulos_1_a_3`.
3. La función `ejecutar_materializador_paso(codigo_paso, proyecto, datos_validados, ...)` busca el despachador en el mapa y lo ejecuta pasándole los argumentos tipados.

## 4. Componentes y Funciones Clave
* `ejecutar_materializador_paso(...)`: Despachador de ejecución de materializadores.
* `MATERIALIZADORES`: Mapa de despacho paso -> función de persistencia.

## 5. Relaciones con Otras Capas y Tablas
* **Invocador:** Llamado por [`backend/thesis/services/pasos.py`](../../backend/thesis/services/pasos.py).
* **Implementación:** Delega en [`consistencia.py`](../../backend/thesis/services/materializadores_pasos/consistencia.py).
