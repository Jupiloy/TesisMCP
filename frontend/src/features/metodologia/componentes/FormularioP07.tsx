import type {
  DimensionJustificacion,
  SalidaP07,
} from "../../../lib/api/cliente"

const DIMENSIONES_ORDEN: Array<{
  codigo: DimensionJustificacion["dimension"]
  titulo: string
  descripcion: string
}> = [
  {
    codigo: "TEORICA",
    titulo: "Justificación Teórica",
    descripcion:
      "Aporte al cuerpo de conocimientos, contraste o enriquecimiento de teorías existentes.",
  },
  {
    codigo: "PRACTICA",
    titulo: "Justificación Práctica",
    descripcion:
      "Resolución directa de problemas operativos, reducción de costos o mejora de procesos.",
  },
  {
    codigo: "METODOLOGICA",
    titulo: "Justificación Metodológica",
    descripcion:
      "Aporte de nuevos instrumentos, técnicas de recolección, métricas o modelos algorítmicos.",
  },
  {
    codigo: "SOCIAL",
    titulo: "Justificación Social",
    descripcion:
      "Beneficio a la comunidad, usuarios finales, estudiantes, empresas o grupos de interés.",
  },
]

export const salidaP07Inicial = (): SalidaP07 => ({
  justificaciones: [
    { dimension: "TEORICA", argumento: "" },
    { dimension: "PRACTICA", argumento: "" },
    { dimension: "METODOLOGICA", argumento: "" },
    { dimension: "SOCIAL", argumento: "" },
  ],
  resumen_ejecutivo: "",
})

interface FormularioP07Props {
  datos: SalidaP07
  alCambiarDatos: (nuevosDatos: SalidaP07) => void
  deshabilitado?: boolean
}

export default function FormularioP07({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP07Props) {
  function actualizarArgumento(
    dimension: DimensionJustificacion["dimension"],
    nuevoArgumento: string,
  ) {
    const nuevas = datos.justificaciones.map((item) =>
      item.dimension === dimension
        ? { ...item, argumento: nuevoArgumento }
        : item,
    )
    alCambiarDatos({ ...datos, justificaciones: nuevas })
  }

  // Asegurar que siempre existan las 4 dimensiones requeridas
  const mapaArgumentos = new Map(
    datos.justificaciones.map((j) => [j.dimension, j.argumento]),
  )

  const resumenValido =
    datos.resumen_ejecutivo.trim().length >= 80 &&
    datos.resumen_ejecutivo.trim().length <= 600

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P07: Justificación de la investigación</h2>
          <p>
            Argumentar rigurosamente las cuatro dimensiones metodológicas
            (mínimo 60 y máximo 800 caracteres cada una) y redactar un resumen
            ejecutivo (80 a 600 caracteres).
          </p>
        </div>
      </div>

      {/* Tarjetas de las 4 dimensiones */}
      <div className="rejilla-dimensiones-p07">
        {DIMENSIONES_ORDEN.map(({ codigo, titulo, descripcion }) => {
          const argumento = mapaArgumentos.get(codigo) ?? ""
          const longitud = argumento.length
          const cumple = longitud >= 60 && longitud <= 800

          return (
            <fieldset key={codigo} className="tarjeta-dimension">
              <legend className="eyebrow blue">{titulo}</legend>
              <p className="descripcion-dimension">{descripcion}</p>
              <label>
                Argumento ({codigo})
                <textarea
                  required
                  minLength={60}
                  maxLength={800}
                  value={argumento}
                  onChange={(e) => actualizarArgumento(codigo, e.target.value)}
                  disabled={deshabilitado}
                  placeholder={`Redacta la justificación ${codigo.toLowerCase()} (mínimo 60 caracteres)…`}
                  rows={4}
                />
              </label>
              <div className="indicadores-dimension">
                <span
                  className={`tag-componente ${
                    cumple ? "valido" : "pendiente"
                  }`}
                >
                  {cumple ? "✓ Cumple requisitos" : "○ Mín. 60 caracteres"}
                </span>
                <span className="caracteres-ayuda">
                  {longitud} / 800 caracteres
                </span>
              </div>
            </fieldset>
          )
        })}
      </div>

      {/* Resumen Ejecutivo */}
      <div className="seccion-resumen-ejecutivo">
        <label className="campo-ancho">
          <span className="eyebrow">RESUMEN EJECUTIVO DE JUSTIFICACIÓN (80 a 600 caracteres)</span>
          <textarea
            required
            minLength={80}
            maxLength={600}
            value={datos.resumen_ejecutivo}
            onChange={(e) =>
              alCambiarDatos({ ...datos, resumen_ejecutivo: e.target.value })
            }
            disabled={deshabilitado}
            placeholder="Sintetiza la relevancia integral de la tesis y su impacto esperado en el contexto profesional y académico…"
            rows={4}
          />
          <div className="indicadores-pregunta">
            <span
              className={`tag-componente ${
                resumenValido ? "valido" : "pendiente"
              }`}
            >
              {resumenValido ? "✓ Longitud válida" : "○ Mínimo 80 caracteres"}
            </span>
            <span className="caracteres-ayuda">
              {datos.resumen_ejecutivo.length} / 600 caracteres
            </span>
          </div>
        </label>
      </div>
    </section>
  )
}
