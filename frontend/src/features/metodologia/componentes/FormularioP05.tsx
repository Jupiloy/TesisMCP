import type { SalidaP05 } from "../../../lib/api/cliente"

const contarParrafos = (texto: string): number =>
  texto
    .split("\n\n")
    .map((parrafo) => parrafo.trim())
    .filter(Boolean).length

const contarPalabras = (texto: string): number =>
  texto.trim().split(/\s+/).filter(Boolean).length

export const salidaP05Inicial = (): SalidaP05 => ({
  contenido_markdown: "",
  num_parrafos: 0,
  palabras_totales: 0,
})

export function normalizarSalidaP05(
  datos?: Partial<SalidaP05> | null,
): SalidaP05 {
  const base = salidaP05Inicial()
  if (!datos) return base
  const texto = datos.contenido_markdown ?? base.contenido_markdown
  return {
    contenido_markdown: texto,
    num_parrafos:
      typeof datos.num_parrafos === "number"
        ? datos.num_parrafos
        : contarParrafos(texto),
    palabras_totales:
      typeof datos.palabras_totales === "number"
        ? datos.palabras_totales
        : contarPalabras(texto),
  }
}

interface FormularioP05Props {
  datos: SalidaP05
  alCambiarDatos: (nuevosDatos: SalidaP05) => void
  deshabilitado?: boolean
  contenidoNarrativo?: string
  alSincronizarNarrativo?: (texto: string) => void
}

export default function FormularioP05({
  datos,
  alCambiarDatos,
  deshabilitado = false,
  contenidoNarrativo = "",
  alSincronizarNarrativo,
}: FormularioP05Props) {
  const datosSeguros = normalizarSalidaP05(datos)

  function actualizarContenido(nuevoTexto: string) {
    const parrafos = contarParrafos(nuevoTexto)
    const palabras = contarPalabras(nuevoTexto)
    alCambiarDatos({
      ...datosSeguros,
      contenido_markdown: nuevoTexto,
      num_parrafos: parrafos,
      palabras_totales: palabras,
    })
  }

  function copiarDesdeNarrativo() {
    if (!contenidoNarrativo) return
    actualizarContenido(contenidoNarrativo)
  }

  function enviarANarrativo() {
    if (alSincronizarNarrativo && datosSeguros.contenido_markdown) {
      alSincronizarNarrativo(datosSeguros.contenido_markdown)
    }
  }

  const parrafosReales = contarParrafos(datosSeguros.contenido_markdown)
  const palabrasReales = contarPalabras(datosSeguros.contenido_markdown)
  const caracteresReales = datosSeguros.contenido_markdown.length

  const cumpleParrafos = parrafosReales >= 3
  const cumplePalabras = palabrasReales >= 250 && palabrasReales <= 1200
  const cumpleCaracteres = caracteresReales >= 500

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P05: Redacción de la Introducción</h2>
          <p>
            Redacta la introducción académica del Capítulo 1 en prosa continua.
            Debe estructurarse en al menos 3 párrafos separados por doble salto de
            línea (\n\n), contener entre 250 y 1200 palabras, y superar 500
            caracteres.
          </p>
        </div>
        <div className="acciones-sincronizacion">
          {contenidoNarrativo && (
            <button
              type="button"
              className="button button-secondary boton-pequeno"
              onClick={copiarDesdeNarrativo}
              disabled={deshabilitado}
              title="Copiar el texto del panel lateral de contenido narrativo a este formulario"
            >
              ↓ Traer de narrativo
            </button>
          )}
          {alSincronizarNarrativo && (
            <button
              type="button"
              className="button button-secondary boton-pequeno"
              onClick={enviarANarrativo}
              disabled={deshabilitado || !datosSeguros.contenido_markdown}
              title="Copiar este texto estructurado al panel de contenido narrativo"
            >
              ↑ Copiar a narrativo
            </button>
          )}
        </div>
      </div>

      <div className="lista-temas">
        <label className="campo-ancho">
          Texto completo de la Introducción (Markdown)
          <textarea
            className="editor-narrativo"
            required
            minLength={500}
            value={datosSeguros.contenido_markdown}
            onChange={(e) => actualizarContenido(e.target.value)}
            disabled={deshabilitado}
            placeholder="Párrafo 1: Contexto general de la investigación…&#10;&#10;Párrafo 2: Problema y motivación metodológica…&#10;&#10;Párrafo 3: Objetivos y estructura del trabajo…"
            rows={12}
          />
        </label>

        {/* Indicadores en tiempo real de cumplimiento de reglas de P05 */}
        <div className="panel-metricas-p05">
          <div
            className={`tarjeta-metrica ${
              cumpleParrafos ? "metrica-ok" : "metrica-alerta"
            }`}
          >
            <span className="etiqueta-metrica">Párrafos (\n\n)</span>
            <strong className="valor-metrica">
              {parrafosReales} / 3 mín.
            </strong>
            <small>{cumpleParrafos ? "Cumplido" : "Requiere ≥ 3 párrafos"}</small>
          </div>

          <div
            className={`tarjeta-metrica ${
              cumplePalabras ? "metrica-ok" : "metrica-alerta"
            }`}
          >
            <span className="etiqueta-metrica">Palabras totales</span>
            <strong className="valor-metrica">
              {palabrasReales} / 250 - 1200
            </strong>
            <small>
              {cumplePalabras
                ? "Rango válido"
                : palabrasReales < 250
                  ? "Faltan palabras"
                  : "Supera el límite"}
            </small>
          </div>

          <div
            className={`tarjeta-metrica ${
              cumpleCaracteres ? "metrica-ok" : "metrica-alerta"
            }`}
          >
            <span className="etiqueta-metrica">Caracteres</span>
            <strong className="valor-metrica">
              {caracteresReales} / 500 mín.
            </strong>
            <small>{cumpleCaracteres ? "Cumplido" : "Requiere ≥ 500"}</small>
          </div>
        </div>
      </div>
    </section>
  )
}
