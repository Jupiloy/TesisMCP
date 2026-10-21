import type { SalidaP11, TipoInvestigacion } from "../../../lib/api/cliente"

interface FormularioP11Props {
  datos: SalidaP11
  alCambiarDatos: (nuevosDatos: SalidaP11) => void
  deshabilitado?: boolean
}

export const TIPOS_INVESTIGACION_OPCIONES: {
  valor: TipoInvestigacion
  etiqueta: string
  descripcion: string
}[] = [
  {
    valor: "APLICADA",
    etiqueta: "Aplicada",
    descripcion:
      "Aplica conocimientos científicos para resolver un problema práctico o tecnológico concreto.",
  },
  {
    valor: "BASICA",
    etiqueta: "Básica",
    descripcion:
      "Busca ampliar el conocimiento teórico y los principios científicos fundamentales.",
  },
  {
    valor: "DESCRIPTIVA",
    etiqueta: "Descriptiva",
    descripcion:
      "Identifica y caracteriza las propiedades y perfiles de personas, grupos o sistemas.",
  },
  {
    valor: "CORRELACIONAL",
    etiqueta: "Correlacional",
    descripcion:
      "Evalúa el grado de relación estadística o asociación existente entre dos o más variables.",
  },
  {
    valor: "EXPLICATIVA",
    etiqueta: "Explicativa",
    descripcion:
      "Determina las causas de los fenómenos físicos o sociales y sus relaciones causa-efecto.",
  },
]

export function salidaP11Inicial(): SalidaP11 {
  return {
    tipo_investigacion: "",
    hipotesis_general: "",
    hipotesis_especificas: ["", ""],
    variable_independiente: "",
    variable_dependiente: "",
  }
}

export default function FormularioP11({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP11Props) {
  const tipo = datos?.tipo_investigacion ?? ""
  const vi = datos?.variable_independiente ?? ""
  const vd = datos?.variable_dependiente ?? ""
  const hipGeneral = datos?.hipotesis_general ?? ""
  const hipEspecificas = datos?.hipotesis_especificas ?? []

  function seleccionarTipo(nuevoTipo: TipoInvestigacion) {
    if (deshabilitado) return
    alCambiarDatos({
      ...datos,
      tipo_investigacion: nuevoTipo,
    })
  }

  function actualizarVI(texto: string) {
    alCambiarDatos({
      ...datos,
      variable_independiente: texto,
    })
  }

  function actualizarVD(texto: string) {
    alCambiarDatos({
      ...datos,
      variable_dependiente: texto,
    })
  }

  function actualizarHipGeneral(texto: string) {
    alCambiarDatos({
      ...datos,
      hipotesis_general: texto,
    })
  }

  function actualizarHipEspecifica(indice: number, texto: string) {
    const lista = [...hipEspecificas]
    lista[indice] = texto
    alCambiarDatos({
      ...datos,
      hipotesis_especificas: lista,
    })
  }

  function agregarHipEspecifica() {
    if (hipEspecificas.length >= 4) return
    alCambiarDatos({
      ...datos,
      hipotesis_especificas: [...hipEspecificas, ""],
    })
  }

  function eliminarHipEspecifica(indice: number) {
    if (hipEspecificas.length <= 2) return
    const lista = hipEspecificas.filter((_, i) => i !== indice)
    alCambiarDatos({
      ...datos,
      hipotesis_especificas: lista,
    })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="formulario-cabecera">
        <div>
          <h2>Paso P11 · Hipótesis y Variables de Investigación</h2>
          <p>
            Defina el tipo metodológico de investigación, precise las variables
            independiente (causa) y dependiente (efecto), y formule la hipótesis
            general junto con sus hipótesis específicas derivadas.
          </p>
        </div>
      </div>

      <div className="bloque-tipo-investigacion">
        <label>
          <strong>Tipo de Investigación</strong>
        </label>
        <div className="grid-tipos-investigacion">
          {TIPOS_INVESTIGACION_OPCIONES.map((opcion) => {
            const estaSeleccionado = tipo === opcion.valor
            return (
              <button
                key={opcion.valor}
                type="button"
                className={`tarjeta-tipo-inv ${
                  estaSeleccionado ? "seleccionado" : ""
                }`}
                onClick={() => seleccionarTipo(opcion.valor)}
                disabled={deshabilitado}
              >
                <div className="encabezado-tipo">
                  <strong>{opcion.etiqueta}</strong>
                  {estaSeleccionado && <span className="check-tipo">✓</span>}
                </div>
                <p>{opcion.descripcion}</p>
              </button>
            )
          })}
        </div>
      </div>

      <div className="grid-variables-estudio">
        <div className="tarjeta-variable vi">
          <div className="campo-encabezado">
            <label htmlFor="variable-independiente">
              <strong>Variable Independiente (VI)</strong> (Causa / Propuesta)
            </label>
            <span className="contador-caracteres">{vi.length} / 120</span>
          </div>
          <input
            id="variable-independiente"
            type="text"
            minLength={3}
            maxLength={120}
            value={vi}
            onChange={(e) => actualizarVI(e.target.value)}
            disabled={deshabilitado}
            placeholder="Ej: Arquitectura de microservicios"
            required
          />
          <small className="ayuda-campo">
            Factor experimental, sistema, técnica o tratamiento introducido.
          </small>
        </div>

        <div className="tarjeta-variable vd">
          <div className="campo-encabezado">
            <label htmlFor="variable-dependiente">
              <strong>Variable Dependiente (VD)</strong> (Efecto / Resultado)
            </label>
            <span className="contador-caracteres">{vd.length} / 120</span>
          </div>
          <input
            id="variable-dependiente"
            type="text"
            minLength={3}
            maxLength={120}
            value={vd}
            onChange={(e) => actualizarVD(e.target.value)}
            disabled={deshabilitado}
            placeholder="Ej: Rendimiento del procesamiento concurrente"
            required
          />
          <small className="ayuda-campo">
            Propiedad o indicador que se espera modificar, medir o evaluar.
          </small>
        </div>
      </div>

      <div className="campo-grupo">
        <div className="campo-encabezado">
          <label htmlFor="hipotesis-general">
            <strong>Hipótesis General</strong> (15 a 300 caracteres)
          </label>
          <span className="contador-caracteres">{hipGeneral.length} / 300</span>
        </div>
        <textarea
          id="hipotesis-general"
          rows={3}
          minLength={15}
          maxLength={300}
          value={hipGeneral}
          onChange={(e) => actualizarHipGeneral(e.target.value)}
          disabled={deshabilitado}
          placeholder="Ej: La implementación de VI mejora significativamente la VD..."
          required
        />
      </div>

      <div className="seccion-especificos">
        <div className="campo-encabezado">
          <label>
            <strong>Hipótesis Específicas</strong> (mínimo 2, máximo 4)
          </label>
          <button
            type="button"
            className="boton-secundario boton-chico"
            onClick={agregarHipEspecifica}
            disabled={deshabilitado || hipEspecificas.length >= 4}
          >
            + Agregar Hipótesis Específica
          </button>
        </div>

        {hipEspecificas.map((hip, indice) => (
          <div key={indice} className="item-especifico-caja">
            <div className="campo-encabezado">
              <span className="numero-item">
                Hipótesis Específica #{indice + 1}
              </span>
              <div className="indicadores-validacion">
                <span className="contador-caracteres">{hip.length} car.</span>
                {hipEspecificas.length > 2 && (
                  <button
                    type="button"
                    className="boton-eliminar-item"
                    onClick={() => eliminarHipEspecifica(indice)}
                    disabled={deshabilitado}
                    title="Eliminar esta hipótesis específica"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            <textarea
              rows={2}
              minLength={15}
              maxLength={300}
              value={hip}
              onChange={(e) => actualizarHipEspecifica(indice, e.target.value)}
              disabled={deshabilitado}
              placeholder="Ej: La dimensión X de la VI reduce el tiempo de..."
              required
            />
          </div>
        ))}
      </div>
    </section>
  )
}
