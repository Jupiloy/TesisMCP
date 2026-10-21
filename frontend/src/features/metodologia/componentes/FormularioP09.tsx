import {
  VERBOS_BLOOM_PERMITIDOS,
  type SalidaP09,
  type VerboBloom,
} from "../../../lib/api/cliente"
import CampoTextoConContador from "../../../components/comunes/CampoTextoConContador"
import ListaDinamicaItems from "../../../components/comunes/ListaDinamicaItems"
import { cn } from "../../../lib/utils"

interface FormularioP09Props {
  datos: SalidaP09
  alCambiarDatos: (nuevosDatos: SalidaP09) => void
  deshabilitado?: boolean
}

export function salidaP09Inicial(): SalidaP09 {
  return {
    objetivo_general: "",
    objetivos_especificos: ["", ""],
  }
}

export function extraerPrimerVerbo(texto: string): string {
  const palabras = texto.trim().split(/\s+/)
  if (!palabras[0]) return ""
  return palabras[0].toUpperCase().replace(/[:,;.]/g, "")
}

export function esVerboBloomValido(texto: string): boolean {
  const verbo = extraerPrimerVerbo(texto)
  return (VERBOS_BLOOM_PERMITIDOS as readonly string[]).includes(verbo)
}

export default function FormularioP09({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP09Props) {
  const objetivoGeneral = datos?.objetivo_general ?? ""
  const objetivosEspecificos = datos?.objetivos_especificos ?? []

  const verboGeneral = extraerPrimerVerbo(objetivoGeneral)
  const esGeneralValido = esVerboBloomValido(objetivoGeneral)

  function aplicarVerboGeneral(verbo: VerboBloom) {
    if (deshabilitado) return
    const partes = objetivoGeneral.trim().split(/\s+/)
    if (partes.length <= 1) {
      alCambiarDatos({ ...datos, objetivo_general: `${verbo} ` })
    } else {
      partes[0] = verbo
      alCambiarDatos({ ...datos, objetivo_general: partes.join(" ") })
    }
  }

  function aplicarVerboEspecifico(indice: number, verbo: VerboBloom) {
    if (deshabilitado) return
    const lista = [...objetivosEspecificos]
    const partes = (lista[indice] ?? "").trim().split(/\s+/)
    if (partes.length <= 1) {
      lista[indice] = `${verbo} `
    } else {
      partes[0] = verbo
      lista[indice] = partes.join(" ")
    }
    alCambiarDatos({ ...datos, objetivos_especificos: lista })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="formulario-cabecera">
        <div>
          <h2>Paso P09 · Objetivos de Investigación</h2>
          <p>
            Formule el objetivo general y los objetivos específicos iniciando
            obligatoriamente con un verbo autorizado de la Taxonomía de Bloom.
          </p>
        </div>
      </div>

      {/* Guía superior de verbos de Bloom */}
      <div className="bloque-bloom-guia">
        <span className="etiqueta-bloom-titulo">
          Verbos de Bloom Autorizados:
        </span>
        <div className="grupo-verbos-bloom">
          {VERBOS_BLOOM_PERMITIDOS.map((verbo) => (
            <button
              key={verbo}
              type="button"
              className={cn(
                "chip-bloom",
                verboGeneral === verbo && "chip-bloom-activo",
              )}
              onClick={() => aplicarVerboGeneral(verbo)}
              disabled={deshabilitado}
              title={`Asignar ${verbo} al objetivo general`}
            >
              {verbo}
            </button>
          ))}
        </div>
      </div>

      {/* Objetivo General con CampoTextoConContador */}
      <CampoTextoConContador
        id="objetivo-general"
        etiqueta="Objetivo General"
        subetiqueta="(15 a 250 caracteres)"
        valor={objetivoGeneral}
        alCambiar={(nuevo) =>
          alCambiarDatos({ ...datos, objetivo_general: nuevo })
        }
        longitudMin={15}
        longitudMax={250}
        filas={3}
        placeholder="Ej: DETERMINAR la relación entre..."
        deshabilitado={deshabilitado}
        formatoInvalido={!esGeneralValido}
        mensajeInvalido={
          esGeneralValido
            ? `✓ Verbo Bloom: ${verboGeneral}`
            : "⚠ Inicie con verbo de Bloom"
        }
      />

      {/* Objetivos Específicos con ListaDinamicaItems */}
      <ListaDinamicaItems
        titulo="Objetivos Específicos"
        subtitulo="Mínimo 2, máximo 4 objetivos. Cada uno debe iniciar con un verbo de Bloom."
        etiquetaItem={(i) => `Objetivo Específico #${i + 1}`}
        items={objetivosEspecificos}
        alCambiarItems={(nuevos) =>
          alCambiarDatos({ ...datos, objetivos_especificos: nuevos })
        }
        minimo={2}
        maximo={4}
        longitudMin={15}
        longitudMax={250}
        placeholderItem="Ej: ANALIZAR el impacto del desacoplamiento..."
        itemNuevoDefecto=""
        deshabilitado={deshabilitado}
        validarItem={(texto) => {
          const valido = esVerboBloomValido(texto)
          const verbo = extraerPrimerVerbo(texto)
          return {
            esValido: valido,
            mensaje: valido ? `✓ ${verbo}` : "Requiere verbo Bloom",
          }
        }}
        renderControlesItem={(indice, item) => {
          const verboActual = extraerPrimerVerbo(item)
          return (
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[10px] text-slate-500 font-medium">
                Asignar verbo:
              </span>
              {VERBOS_BLOOM_PERMITIDOS.slice(0, 8).map((v) => (
                <button
                  key={v}
                  type="button"
                  className={cn(
                    "text-[10px] px-1.5 py-0.5 rounded border transition-colors",
                    verboActual === v
                      ? "bg-blue-600 text-white border-blue-600 font-semibold"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-slate-100",
                  )}
                  onClick={() => aplicarVerboEspecifico(indice, v)}
                  disabled={deshabilitado}
                >
                  {v}
                </button>
              ))}
            </div>
          )
        }}
      />
    </section>
  )
}
