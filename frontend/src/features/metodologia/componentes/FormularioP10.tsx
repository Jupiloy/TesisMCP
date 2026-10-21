import type { SalidaP10 } from "../../../lib/api/cliente"
import CampoTextoConContador from "../../../components/comunes/CampoTextoConContador"
import ListaDinamicaItems from "../../../components/comunes/ListaDinamicaItems"

interface FormularioP10Props {
  datos: SalidaP10
  alCambiarDatos: (nuevosDatos: SalidaP10) => void
  deshabilitado?: boolean
}

export function salidaP10Inicial(): SalidaP10 {
  return {
    pregunta_general: "",
    preguntas_especificas: ["", ""],
  }
}

export function tieneFormatoPreguntaValido(texto: string): boolean {
  const limpio = texto.trim()
  return (
    limpio.startsWith("¿") &&
    limpio.endsWith("?") &&
    limpio.length >= 15 &&
    limpio.length <= 250
  )
}

export function formatearConSignosPregunta(texto: string): string {
  let limpio = texto.trim()
  if (!limpio) return limpio
  if (!limpio.startsWith("¿")) {
    limpio = `¿${limpio}`
  }
  if (!limpio.endsWith("?")) {
    limpio = `${limpio}?`
  }
  return limpio
}

export default function FormularioP10({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP10Props) {
  const preguntaGeneral = datos?.pregunta_general ?? ""
  const preguntasEspecificas = datos?.preguntas_especificas ?? []

  const generalValida = tieneFormatoPreguntaValido(preguntaGeneral)

  function ajustarSignosGeneral() {
    if (deshabilitado) return
    alCambiarDatos({
      ...datos,
      pregunta_general: formatearConSignosPregunta(preguntaGeneral),
    })
  }

  function ajustarSignosEspecifica(indice: number) {
    if (deshabilitado) return
    const lista = [...preguntasEspecificas]
    lista[indice] = formatearConSignosPregunta(lista[indice] ?? "")
    alCambiarDatos({
      ...datos,
      preguntas_especificas: lista,
    })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="formulario-cabecera">
        <div>
          <h2>Paso P10 · Preguntas de Investigación Alineadas</h2>
          <p>
            Redacte las preguntas de investigación asegurando correspondencia
            biunívoca con los objetivos y la delimitación. Cada pregunta debe
            abrir con <code>¿</code> y cerrar con <code>?</code>{" "}
            obligatoriamente.
          </p>
        </div>
      </div>

      {/* Pregunta General con CampoTextoConContador */}
      <CampoTextoConContador
        id="pregunta-general"
        etiqueta="Pregunta General de Investigación"
        subetiqueta="(15 a 250 caracteres con signos ¿?)"
        valor={preguntaGeneral}
        alCambiar={(nuevo) =>
          alCambiarDatos({ ...datos, pregunta_general: nuevo })
        }
        longitudMin={15}
        longitudMax={250}
        filas={3}
        placeholder="Ej: ¿De qué manera la solución propuesta impacta en...?"
        deshabilitado={deshabilitado}
        formatoInvalido={!generalValida}
        mensajeInvalido={
          generalValida ? "✓ Formato ¿ ? correcto" : "Requiere signos ¿ y ?"
        }
        accionDerecha={
          !generalValida && (
            <button
              type="button"
              className="text-[11px] font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200 px-2 py-0.5 rounded transition-colors"
              onClick={ajustarSignosGeneral}
              disabled={deshabilitado}
            >
              Añadir signos ¿ ?
            </button>
          )
        }
      />

      {/* Preguntas Específicas con ListaDinamicaItems */}
      <ListaDinamicaItems
        titulo="Preguntas Específicas"
        subtitulo="Mínimo 2, máximo 4 preguntas. Cada una debe abrir con ¿ y cerrar con ?."
        etiquetaItem={(i) => `Pregunta Específica #${i + 1}`}
        items={preguntasEspecificas}
        alCambiarItems={(nuevas) =>
          alCambiarDatos({ ...datos, preguntas_especificas: nuevas })
        }
        minimo={2}
        maximo={4}
        longitudMin={15}
        longitudMax={250}
        placeholderItem="Ej: ¿Cómo influye el factor X en el indicador Y...?"
        itemNuevoDefecto=""
        deshabilitado={deshabilitado}
        validarItem={(texto) => {
          const valida = tieneFormatoPreguntaValido(texto)
          return {
            esValido: valida,
            mensaje: valida ? "✓ Formato ¿ ?" : "Requiere signos ¿ y ?",
          }
        }}
        renderControlesItem={(indice, item) => {
          const valida = tieneFormatoPreguntaValido(item)
          if (valida) return null
          return (
            <button
              type="button"
              className="text-[10px] font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200 px-2 py-0.5 rounded transition-colors"
              onClick={() => ajustarSignosEspecifica(indice)}
              disabled={deshabilitado}
            >
              Añadir signos ¿ ? a esta pregunta
            </button>
          )
        }}
      />
    </section>
  )
}
