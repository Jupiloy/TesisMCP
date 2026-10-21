import type { SalidaP01, TemaCandidato } from "../../../lib/api/cliente"

const separarLineas = (texto: string) =>
  texto
    .split("\n")
    .map((linea) => linea.trim())
    .filter(Boolean)

const unirLineas = (valores: string[]) => valores.join("\n")

export const crearTemaVacio = (id: number): TemaCandidato => ({
  id,
  titulo_tentativo: "",
  pros: [""],
  contras: [""],
  viabilidad_preliminar: "MEDIA",
})

export const salidaP01Inicial = (): SalidaP01 => ({
  temas_propuestos: Array.from({ length: 5 }, (_, indice) =>
    crearTemaVacio(indice + 1),
  ),
  tema_preseleccionado_id: null,
})

export function normalizarSalidaP01(
  datos?: Partial<SalidaP01> | null,
): SalidaP01 {
  const base = salidaP01Inicial()
  if (!datos) return base
  return {
    temas_propuestos:
      Array.isArray(datos.temas_propuestos) && datos.temas_propuestos.length > 0
        ? datos.temas_propuestos
        : base.temas_propuestos,
    tema_preseleccionado_id:
      typeof datos.tema_preseleccionado_id === "number" ||
      datos.tema_preseleccionado_id === null
        ? datos.tema_preseleccionado_id
        : base.tema_preseleccionado_id,
  }
}

interface FormularioP01Props {
  datos: SalidaP01
  alCambiarDatos: (nuevosDatos: SalidaP01) => void
  deshabilitado?: boolean
}

export default function FormularioP01({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP01Props) {
  const datosSeguros = normalizarSalidaP01(datos)

  function actualizarTema(id: number, cambio: Partial<TemaCandidato>) {
    alCambiarDatos({
      ...datosSeguros,
      temas_propuestos: datosSeguros.temas_propuestos.map((tema) =>
        tema.id === id ? { ...tema, ...cambio } : tema,
      ),
    })
  }

  function agregarTema() {
    if (datosSeguros.temas_propuestos.length >= 10) return
    const siguienteId =
      Math.max(...datosSeguros.temas_propuestos.map((tema) => tema.id), 0) + 1
    alCambiarDatos({
      ...datosSeguros,
      temas_propuestos: [
        ...datosSeguros.temas_propuestos,
        crearTemaVacio(siguienteId),
      ],
    })
  }

  function quitarTema(id: number) {
    if (datosSeguros.temas_propuestos.length <= 5) return
    alCambiarDatos({
      temas_propuestos: datosSeguros.temas_propuestos.filter(
        (tema) => tema.id !== id,
      ),
      tema_preseleccionado_id:
        datosSeguros.tema_preseleccionado_id === id
          ? null
          : datosSeguros.tema_preseleccionado_id,
    })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P01</h2>
          <p>El contrato P01 exige entre 5 y 10 temas viables.</p>
        </div>
        <button
          className="button button-secondary"
          type="button"
          onClick={agregarTema}
          disabled={deshabilitado || datosSeguros.temas_propuestos.length >= 10}
        >
          Añadir tema ({datosSeguros.temas_propuestos.length}/10)
        </button>
      </div>
      <div className="lista-temas">
        {datosSeguros.temas_propuestos.map((tema) => (
          <fieldset key={tema.id} className="tema-candidato">
            <legend>Tema {tema.id}</legend>
            <button
              type="button"
              className="quitar-tema"
              onClick={() => quitarTema(tema.id)}
              disabled={deshabilitado || datosSeguros.temas_propuestos.length <= 5}
            >
              Quitar
            </button>
            <label className="campo-ancho">
              Título tentativo (10 a 200 caracteres)
              <input
                required
                minLength={10}
                maxLength={200}
                value={tema.titulo_tentativo}
                onChange={(evento) =>
                  actualizarTema(tema.id, {
                    titulo_tentativo: evento.target.value,
                  })
                }
                disabled={deshabilitado}
              />
            </label>
            <label>
              Pros (uno por línea, mínimo 1)
              <textarea
                required
                value={unirLineas(tema.pros)}
                onChange={(evento) =>
                  actualizarTema(tema.id, {
                    pros: separarLineas(evento.target.value),
                  })
                }
                disabled={deshabilitado}
              />
            </label>
            <label>
              Contras (uno por línea, mínimo 1)
              <textarea
                required
                value={unirLineas(tema.contras)}
                onChange={(evento) =>
                  actualizarTema(tema.id, {
                    contras: separarLineas(evento.target.value),
                  })
                }
                disabled={deshabilitado}
              />
            </label>
            <label>
              Viabilidad preliminar
              <select
                value={tema.viabilidad_preliminar}
                onChange={(evento) =>
                  actualizarTema(tema.id, {
                    viabilidad_preliminar: evento.target
                      .value as TemaCandidato["viabilidad_preliminar"],
                  })
                }
                disabled={deshabilitado}
              >
                <option value="ALTA">ALTA</option>
                <option value="MEDIA">MEDIA</option>
                <option value="BAJA">BAJA</option>
              </select>
            </label>
          </fieldset>
        ))}
      </div>
      <label className="campo-preseleccion">
        Tema preseleccionado (opcional)
        <select
          value={datosSeguros.tema_preseleccionado_id ?? ""}
          onChange={(evento) =>
            alCambiarDatos({
              ...datosSeguros,
              tema_preseleccionado_id: evento.target.value
                ? Number(evento.target.value)
                : null,
            })
          }
          disabled={deshabilitado}
        >
          <option value="">Aún no seleccionar</option>
          {datosSeguros.temas_propuestos.map((tema) => (
            <option key={tema.id} value={tema.id}>
              Tema {tema.id}: {tema.titulo_tentativo || `(Tema ${tema.id})`}
            </option>
          ))}
        </select>
      </label>
    </section>
  )
}
