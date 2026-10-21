import type { SalidaP06 } from "../../../lib/api/cliente"

export const salidaP06Inicial = (): SalidaP06 => ({
  problema_central: "",
  causas_directas: ["", ""],
  efectos_directos: ["", ""],
  pregunta_general: "",
  preguntas_especificas: ["", ""],
})

interface FormularioP06Props {
  datos: SalidaP06
  alCambiarDatos: (nuevosDatos: SalidaP06) => void
  deshabilitado?: boolean
}

function asegurarSignos(texto: string): string {
  let limpio = texto.trim()
  if (!limpio) return "¿?"
  if (!limpio.startsWith("¿")) limpio = `¿${limpio}`
  if (!limpio.endsWith("?")) limpio = `${limpio}?`
  return limpio
}

export default function FormularioP06({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP06Props) {
  // Manejadores para Causas Directas (2 a 5)
  function actualizarCausa(indice: number, valor: string) {
    const nuevas = [...datos.causas_directas]
    nuevas[indice] = valor
    alCambiarDatos({ ...datos, causas_directas: nuevas })
  }

  function agregarCausa() {
    if (datos.causas_directas.length >= 5) return
    alCambiarDatos({
      ...datos,
      causas_directas: [...datos.causas_directas, ""],
    })
  }

  function quitarCausa(indice: number) {
    if (datos.causas_directas.length <= 2) return
    alCambiarDatos({
      ...datos,
      causas_directas: datos.causas_directas.filter((_, i) => i !== indice),
    })
  }

  // Manejadores para Efectos Directos (2 a 5)
  function actualizarEfecto(indice: number, valor: string) {
    const nuevos = [...datos.efectos_directos]
    nuevos[indice] = valor
    alCambiarDatos({ ...datos, efectos_directos: nuevos })
  }

  function agregarEfecto() {
    if (datos.efectos_directos.length >= 5) return
    alCambiarDatos({
      ...datos,
      efectos_directos: [...datos.efectos_directos, ""],
    })
  }

  function quitarEfecto(indice: number) {
    if (datos.efectos_directos.length <= 2) return
    alCambiarDatos({
      ...datos,
      efectos_directos: datos.efectos_directos.filter((_, i) => i !== indice),
    })
  }

  // Manejadores para Preguntas Específicas (2 a 4)
  function actualizarPreguntaEspecifica(indice: number, valor: string) {
    const nuevas = [...datos.preguntas_especificas]
    nuevas[indice] = valor
    alCambiarDatos({ ...datos, preguntas_especificas: nuevas })
  }

  function agregarPreguntaEspecifica() {
    if (datos.preguntas_especificas.length >= 4) return
    alCambiarDatos({
      ...datos,
      preguntas_especificas: [...datos.preguntas_especificas, ""],
    })
  }

  function quitarPreguntaEspecifica(indice: number) {
    if (datos.preguntas_especificas.length <= 2) return
    alCambiarDatos({
      ...datos,
      preguntas_especificas: datos.preguntas_especificas.filter(
        (_, i) => i !== indice,
      ),
    })
  }

  const preguntaGeneralValida =
    datos.pregunta_general.trim().startsWith("¿") &&
    datos.pregunta_general.trim().endsWith("?") &&
    datos.pregunta_general.trim().length >= 20

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P06: Árbol del problema y formulación</h2>
          <p>
            Construye el diagnóstico visual de causas y efectos (2 a 5 de cada
            uno) y formula las preguntas de investigación con signos de
            interrogación `¿?`.
          </p>
        </div>
      </div>

      {/* Árbol Visual del Problema */}
      <div className="arbol-visual-problema">
        {/* Nivel 1: Efectos directos (arriba) */}
        <div className="bloque-arbol bloque-efectos">
          <div className="cabecera-bloque-arbol">
            <span className="eyebrow amber">1. EFECTOS DIRECTOS (2 a 5)</span>
            <button
              type="button"
              className="button button-secondary boton-agregar-pequeno"
              onClick={agregarEfecto}
              disabled={deshabilitado || datos.efectos_directos.length >= 5}
            >
              + Añadir efecto ({datos.efectos_directos.length}/5)
            </button>
          </div>
          <div className="rejilla-nodos-arbol">
            {datos.efectos_directos.map((efecto, idx) => (
              <div key={idx} className="nodo-arbol nodo-efecto">
                <div className="fila-nodo-input">
                  <span className="badge-nodo">E{idx + 1}</span>
                  <input
                    required
                    value={efecto}
                    onChange={(e) => actualizarEfecto(idx, e.target.value)}
                    disabled={deshabilitado}
                    placeholder={`Efecto directo ${idx + 1}…`}
                  />
                  <button
                    type="button"
                    className="quitar-nodo"
                    onClick={() => quitarEfecto(idx)}
                    disabled={
                      deshabilitado || datos.efectos_directos.length <= 2
                    }
                    title="Eliminar efecto"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Conector visual hacia abajo */}
        <div className="conector-flujo-arbol">▲ CONSECUENCIAS DIRECTAS ▲</div>

        {/* Nivel 2: Problema Central (centro) */}
        <div className="bloque-arbol bloque-problema-central">
          <label className="campo-ancho">
            <span className="eyebrow blue">
              2. PROBLEMA CENTRAL (15 a 250 caracteres)
            </span>
            <textarea
              required
              minLength={15}
              maxLength={250}
              className="input-problema-central"
              value={datos.problema_central}
              onChange={(e) =>
                alCambiarDatos({ ...datos, problema_central: e.target.value })
              }
              disabled={deshabilitado}
              placeholder="Describe el núcleo del problema de investigación empírico o técnico…"
              rows={3}
            />
            <span className="caracteres-ayuda">
              {datos.problema_central.length} / 250 caracteres (mínimo 15)
            </span>
          </label>
        </div>

        {/* Conector visual hacia abajo */}
        <div className="conector-flujo-arbol">▼ CAUSAS ORIGINARIAS ▼</div>

        {/* Nivel 3: Causas directas (abajo) */}
        <div className="bloque-arbol bloque-causas">
          <div className="cabecera-bloque-arbol">
            <span className="eyebrow green">3. CAUSAS DIRECTAS (2 a 5)</span>
            <button
              type="button"
              className="button button-secondary boton-agregar-pequeno"
              onClick={agregarCausa}
              disabled={deshabilitado || datos.causas_directas.length >= 5}
            >
              + Añadir causa ({datos.causas_directas.length}/5)
            </button>
          </div>
          <div className="rejilla-nodos-arbol">
            {datos.causas_directas.map((causa, idx) => (
              <div key={idx} className="nodo-arbol nodo-causa">
                <div className="fila-nodo-input">
                  <span className="badge-nodo">C{idx + 1}</span>
                  <input
                    required
                    value={causa}
                    onChange={(e) => actualizarCausa(idx, e.target.value)}
                    disabled={deshabilitado}
                    placeholder={`Causa directa ${idx + 1}…`}
                  />
                  <button
                    type="button"
                    className="quitar-nodo"
                    onClick={() => quitarCausa(idx)}
                    disabled={
                      deshabilitado || datos.causas_directas.length <= 2
                    }
                    title="Eliminar causa"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bloque de Formulación de Preguntas */}
      <div className="seccion-preguntas-p06">
        <label className="campo-ancho">
          <div className="cabecera-campo-pregunta">
            <span>Pregunta General de Investigación (20 a 250 caracteres)</span>
            <button
              type="button"
              className="boton-ayuda-signos"
              onClick={() =>
                alCambiarDatos({
                  ...datos,
                  pregunta_general: asegurarSignos(datos.pregunta_general),
                })
              }
              disabled={deshabilitado}
            >
              Alinear signos ¿ ?
            </button>
          </div>
          <input
            required
            minLength={20}
            maxLength={250}
            value={datos.pregunta_general}
            onChange={(e) =>
              alCambiarDatos({ ...datos, pregunta_general: e.target.value })
            }
            disabled={deshabilitado}
            placeholder="¿De qué manera el protocolo MCP mejora la precisión en la formulación de tesis?"
          />
          <div className="indicadores-pregunta">
            <span
              className={`tag-componente ${
                preguntaGeneralValida ? "valido" : "pendiente"
              }`}
            >
              {preguntaGeneralValida
                ? "✓ Signos y longitud válidos"
                : "○ Requiere ¿?, mín. 20 caracteres"}
            </span>
            <span className="caracteres-ayuda">
              {datos.pregunta_general.length} / 250 caracteres
            </span>
          </div>
        </label>

        <div className="campo-ancho">
          <div className="titulo-seccion-variables">
            <label className="label-sin-margen">
              Preguntas Específicas (2 a 4 preguntas con ¿ ?)
            </label>
            <button
              type="button"
              className="button button-secondary boton-agregar-pequeno"
              onClick={agregarPreguntaEspecifica}
              disabled={
                deshabilitado || datos.preguntas_especificas.length >= 4
              }
            >
              + Añadir pregunta específica ({datos.preguntas_especificas.length}
              /4)
            </button>
          </div>
          <div className="lista-variables-inputs">
            {datos.preguntas_especificas.map((pregunta, idx) => {
              const valida =
                pregunta.trim().startsWith("¿") && pregunta.trim().endsWith("?")
              return (
                <div key={idx} className="fila-pregunta-especifica">
                  <div className="contenedor-input-pregunta">
                    <input
                      required
                      value={pregunta}
                      onChange={(e) =>
                        actualizarPreguntaEspecifica(idx, e.target.value)
                      }
                      disabled={deshabilitado}
                      placeholder={`¿Pregunta específica ${idx + 1}?`}
                    />
                    <button
                      type="button"
                      className="boton-formatear-signo"
                      onClick={() =>
                        actualizarPreguntaEspecifica(
                          idx,
                          asegurarSignos(pregunta),
                        )
                      }
                      disabled={deshabilitado}
                      title="Envolver con signos ¿?"
                    >
                      ¿?
                    </button>
                  </div>
                  <button
                    type="button"
                    className="quitar-tema"
                    onClick={() => quitarPreguntaEspecifica(idx)}
                    disabled={
                      deshabilitado || datos.preguntas_especificas.length <= 2
                    }
                  >
                    Quitar
                  </button>
                  {!valida && (
                    <span className="alerta-pregunta-invalida">
                      Debe iniciar con ¿ y terminar con ?
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
