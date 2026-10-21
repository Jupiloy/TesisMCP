import type {
  CriterioEvaluacion,
  EvaluacionTema,
  SalidaP02,
} from "../../../lib/api/cliente"

const crearEvaluacionInicial = (
  temaId: number,
  titulo: string = "",
): EvaluacionTema => ({
  tema_id: temaId,
  titulo,
  puntajes: {
    acceso_a_datos: 0,
    relevancia_profesional: 0,
    brecha_conocimiento: 0,
    recursos_disponibles: 0,
  },
  puntaje_total: 0,
  justificacion_eleccion: "",
})

export const salidaP02Inicial = (): SalidaP02 => {
  const temas = [
    crearEvaluacionInicial(1),
    crearEvaluacionInicial(2),
    crearEvaluacionInicial(3),
  ]
  return {
    matriz_comparativa: temas,
    tema_ganador_id: 0,
    tema_ganador_titulo: "",
  }
}

export function normalizarSalidaP02(
  datos?: Partial<SalidaP02> | null,
): SalidaP02 {
  const base = salidaP02Inicial()
  if (!datos) return base

  const matrizValida =
    Array.isArray(datos.matriz_comparativa) &&
    datos.matriz_comparativa.length > 0
      ? datos.matriz_comparativa.map((t, idx) => ({
          tema_id: typeof t?.tema_id === "number" ? t.tema_id : idx + 1,
          titulo: t?.titulo ?? "",
          puntajes: {
            acceso_a_datos:
              typeof t?.puntajes?.acceso_a_datos === "number"
                ? t.puntajes.acceso_a_datos
                : 0,
            relevancia_profesional:
              typeof t?.puntajes?.relevancia_profesional === "number"
                ? t.puntajes.relevancia_profesional
                : 0,
            brecha_conocimiento:
              typeof t?.puntajes?.brecha_conocimiento === "number"
                ? t.puntajes.brecha_conocimiento
                : 0,
            recursos_disponibles:
              typeof t?.puntajes?.recursos_disponibles === "number"
                ? t.puntajes.recursos_disponibles
                : 0,
          },
          puntaje_total:
            typeof t?.puntaje_total === "number" ? t.puntaje_total : 0,
          justificacion_eleccion: t?.justificacion_eleccion ?? "",
        }))
      : base.matriz_comparativa

  const ganadorId =
    typeof datos.tema_ganador_id === "number"
      ? datos.tema_ganador_id
      : base.tema_ganador_id

  const ganadorTitulo = datos.tema_ganador_titulo ?? base.tema_ganador_titulo

  return {
    matriz_comparativa: matrizValida,
    tema_ganador_id: ganadorId,
    tema_ganador_titulo: ganadorTitulo,
  }
}

interface FormularioP02Props {
  datos: SalidaP02
  alCambiarDatos: (nuevosDatos: SalidaP02) => void
  deshabilitado?: boolean
}

export default function FormularioP02({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP02Props) {
  const datosSeguros = normalizarSalidaP02(datos)

  function actualizarTema(indice: number, cambio: Partial<EvaluacionTema>) {
    const nuevaMatriz = datosSeguros.matriz_comparativa.map((evaluacion, i) => {
      if (i !== indice) return evaluacion
      const actualizado = { ...evaluacion, ...cambio }
      return actualizado
    })

    // Sincronizar título del ganador si el tema editado es el ganador
    const temaEditado = nuevaMatriz[indice]
    const esGanador = temaEditado.tema_id === datosSeguros.tema_ganador_id
    alCambiarDatos({
      ...datosSeguros,
      matriz_comparativa: nuevaMatriz,
      tema_ganador_titulo: esGanador
        ? temaEditado.titulo
        : datosSeguros.tema_ganador_titulo,
    })
  }

  function actualizarPuntaje(
    indice: number,
    criterio: keyof CriterioEvaluacion,
    valor: number,
  ) {
    const temaActual = datosSeguros.matriz_comparativa[indice]
    const nuevosPuntajes = {
      ...temaActual.puntajes,
      [criterio]: valor,
    }
    const nuevoTotal =
      nuevosPuntajes.acceso_a_datos +
      nuevosPuntajes.relevancia_profesional +
      nuevosPuntajes.brecha_conocimiento +
      nuevosPuntajes.recursos_disponibles

    actualizarTema(indice, {
      puntajes: nuevosPuntajes,
      puntaje_total: nuevoTotal,
    })
  }

  function seleccionarGanador(temaId: number) {
    const tema = datosSeguros.matriz_comparativa.find(
      (t) => t.tema_id === temaId,
    )
    if (!tema) return
    alCambiarDatos({
      ...datosSeguros,
      tema_ganador_id: tema.tema_id,
      tema_ganador_titulo: tema.titulo,
    })
  }

  const maximoPuntaje = Math.max(
    ...datosSeguros.matriz_comparativa.map((t) => t.puntaje_total),
    0,
  )
  const temaGanador = datosSeguros.matriz_comparativa.find(
    (t) => t.tema_id === datosSeguros.tema_ganador_id,
  )
  const ganadorValido =
    temaGanador && temaGanador.puntaje_total >= maximoPuntaje

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P02: Matriz de factibilidad</h2>
          <p>
            Compara exactamente 3 temas evaluando de 1 a 5 cada criterio. El
            puntaje total se calcula automáticamente (4 a 20).
          </p>
        </div>
      </div>

      <div className="lista-temas">
        {datosSeguros.matriz_comparativa.map((tema, indice) => (
          <fieldset
            key={tema.tema_id}
            className="tema-candidato tema-evaluacion"
          >
            <legend>
              Evaluación {indice + 1} (Tema ID: {tema.tema_id})
            </legend>
            <div className="campo-ancho fila-id-titulo">
              <label className="campo-id-tema">
                ID Tema (1-10)
                <input
                  type="number"
                  min={1}
                  max={10}
                  required
                  value={tema.tema_id}
                  onChange={(e) => {
                    const nuevoId = Number(e.target.value)
                    const eraGanador =
                      tema.tema_id === datosSeguros.tema_ganador_id
                    const nuevaMatriz = datosSeguros.matriz_comparativa.map(
                      (t, i) => (i === indice ? { ...t, tema_id: nuevoId } : t),
                    )
                    alCambiarDatos({
                      ...datosSeguros,
                      matriz_comparativa: nuevaMatriz,
                      tema_ganador_id: eraGanador
                        ? nuevoId
                        : datosSeguros.tema_ganador_id,
                    })
                  }}
                  disabled={deshabilitado}
                />
              </label>
              <label className="campo-titulo-tema">
                Título del tema evaluado (mínimo 10 caracteres)
                <input
                  required
                  minLength={10}
                  value={tema.titulo}
                  onChange={(e) =>
                    actualizarTema(indice, { titulo: e.target.value })
                  }
                  disabled={deshabilitado}
                />
              </label>
            </div>

            <div className="campo-ancho rejilla-criterios">
              <label>
                Acceso a datos (1-5)
                <select
                  value={tema.puntajes.acceso_a_datos}
                  onChange={(e) =>
                    actualizarPuntaje(
                      indice,
                      "acceso_a_datos",
                      Number(e.target.value),
                    )
                  }
                  disabled={deshabilitado}
                >
                  <option value={0} disabled>
                    Selecciona un puntaje
                  </option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Relevancia profesional (1-5)
                <select
                  value={tema.puntajes.relevancia_profesional}
                  onChange={(e) =>
                    actualizarPuntaje(
                      indice,
                      "relevancia_profesional",
                      Number(e.target.value),
                    )
                  }
                  disabled={deshabilitado}
                >
                  <option value={0} disabled>
                    Selecciona un puntaje
                  </option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Brecha conocimiento (1-5)
                <select
                  value={tema.puntajes.brecha_conocimiento}
                  onChange={(e) =>
                    actualizarPuntaje(
                      indice,
                      "brecha_conocimiento",
                      Number(e.target.value),
                    )
                  }
                  disabled={deshabilitado}
                >
                  <option value={0} disabled>
                    Selecciona un puntaje
                  </option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Recursos disponibles (1-5)
                <select
                  value={tema.puntajes.recursos_disponibles}
                  onChange={(e) =>
                    actualizarPuntaje(
                      indice,
                      "recursos_disponibles",
                      Number(e.target.value),
                    )
                  }
                  disabled={deshabilitado}
                >
                  <option value={0} disabled>
                    Selecciona un puntaje
                  </option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <div className="resumen-puntaje">
                <small>Puntaje Total</small>
                <strong>{tema.puntaje_total} / 20</strong>
              </div>
            </div>

            <label className="campo-ancho">
              Justificación de la elección (20 a 500 caracteres)
              <textarea
                required
                minLength={20}
                maxLength={500}
                value={tema.justificacion_eleccion}
                onChange={(e) =>
                  actualizarTema(indice, {
                    justificacion_eleccion: e.target.value,
                  })
                }
                disabled={deshabilitado}
                placeholder="Explica la viabilidad y relevancia técnica de este tema candidato…"
              />
              <span className="caracteres-ayuda">
                {tema.justificacion_eleccion.length}/500 caracteres
              </span>
            </label>
          </fieldset>
        ))}
      </div>

      <div className="seccion-ganador">
        <label className="campo-preseleccion">
          Tema ganador oficial
          <select
            value={datosSeguros.tema_ganador_id}
            onChange={(e) => seleccionarGanador(Number(e.target.value))}
            disabled={deshabilitado}
          >
            <option value={0} disabled>
              Selecciona el tema con mayor puntaje
            </option>
            {datosSeguros.matriz_comparativa.map((t) => (
              <option key={t.tema_id} value={t.tema_id}>
                Tema {t.tema_id}: {t.titulo || `(Tema ${t.tema_id})`} —{" "}
                {t.puntaje_total} pts
              </option>
            ))}
          </select>
        </label>
        {!ganadorValido && (
          <p className="aviso-advertencia-campo">
            Atención: El tema ganador debe tener un puntaje total igual o
            superior al de los demás temas ({maximoPuntaje} pts).
          </p>
        )}
      </div>
    </section>
  )
}
