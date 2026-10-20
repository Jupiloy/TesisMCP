# Explicación de Código: `backend/thesis/services/exploration.py`

## 1. Propósito y ¿Qué hace?
Permite registrar y validar la idea preliminar de investigación confirmada por el tesista (`registrar_idea_servicio`) y realizar una exploración automática de literatura científica en OpenAlex sobre dicha idea (`explorar_idea_servicio`).

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Paso Previo a la Formulación:** Antes de redactar el problema o los objetivos, el estudiante debe explorar si existe suficiente literatura científica sobre su tema de interés.
* **Control de Versión:** Actualiza la idea en `PerfilInvestigacion` aplicando control de concurrencia optimista (`lock_version`).

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. `registrar_idea_servicio`:
   - Verifica pertenencia y rol `OWNER`.
   - Comprueba `expected_version == profile.lock_version`.
   - Actualiza el campo de planteamiento/idea y aumenta `lock_version += 1`.
2. `explorar_idea_servicio`:
   - Toma la idea registrada en el perfil.
   - Consulta OpenAlex extrayendo las obras más relevantes indexadas internacionalmente.

## 4. Componentes y Funciones Clave
* `registrar_idea_servicio(...)`: Guarda la idea temática inicial.
* `explorar_idea_servicio(...)`: Consulta literatura a partir de la idea registrada.

## 5. Relaciones con Otras Capas y Tablas
* **Modelo:** Modifica `PerfilInvestigacion` (`tesis_perfil_investigacion`).
* **Integración:** Consume [`backend/thesis/integrations/openalex.py`](../../backend/thesis/integrations/openalex.py).
* **MCP Tools:** `registrar_idea` y `explorar_idea`.
