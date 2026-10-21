import { useState } from "react"
import type {
  EscalaMedicion,
  FilaOperacionalizacion,
  SalidaP12,
} from "../../../lib/api/cliente"

interface FormularioP12Props {
  datos: SalidaP12
  alCambiarDatos: (nuevosDatos: SalidaP12) => void
  deshabilitado?: boolean
}

export const ESCALAS_MEDICION: {
  valor: EscalaMedicion
  etiqueta: string
  descripcion: string
}[] = [
  {
    valor: "NOMINAL",
    etiqueta: "Nominal",
    descripcion:
      "Categorías sin orden intrínseco (ej. tipo, presencia/ausencia)",
  },
  {
    valor: "ORDINAL",
    etiqueta: "Ordinal",
    descripcion: "Categorías con jerarquía u orden (ej. bajo, medio, alto)",
  },
  {
    valor: "INTERVALO",
    etiqueta: "Intervalo",
    descripcion: "Valores cuantitativos con cero relativo (ej. temperatura °C)",
  },
  {
    valor: "RAZON",
    etiqueta: "Razón",
    descripcion:
      "Valores cuantitativos continuos con cero absoluto (ej. tiempo, tasa)",
  },
]

export function salidaP12Inicial(): SalidaP12 {
  return {
    matriz_operacionalizacion: [
      {
        variable: "",
        definicion_conceptual: "",
        definicion_operacional: "",
        dimensiones: [],
        indicadores: [],
        escala_medicion: "",
      },
    ],
  }
}

export default function FormularioP12({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP12Props) {
  const filas = datos?.matriz_operacionalizacion ?? []
  const [nuevaDimension, setNuevaDimension] = useState<Record<number, string>>(
    {},
  )
  const [nuevoIndicador, setNuevoIndicador] = useState<Record<number, string>>(
    {},
  )

  function actualizarFila(
    indice: number,
    campos: Partial<FilaOperacionalizacion>,
  ) {
    const copia = [...filas]
    copia[indice] = { ...copia[indice], ...campos }
    alCambiarDatos({
      ...datos,
      matriz_operacionalizacion: copia,
    })
  }

  function agregarFila() {
    if (filas.length >= 4) return
    const nueva: FilaOperacionalizacion = {
      variable: "",
      definicion_conceptual: "",
      definicion_operacional: "",
      dimensiones: [],
      indicadores: [],
      escala_medicion: "",
    }
    alCambiarDatos({
      ...datos,
      matriz_operacionalizacion: [...filas, nueva],
    })
  }

  function eliminarFila(indice: number) {
    if (filas.length <= 1) return
    const copia = filas.filter((_, i) => i !== indice)
    alCambiarDatos({
      ...datos,
      matriz_operacionalizacion: copia,
    })
  }

  function agregarDimension(indice: number) {
    const texto = (nuevaDimension[indice] ?? "").trim()
    if (!texto) return
    const fila = filas[indice]
    if (fila.dimensiones.length >= 6) return
    actualizarFila(indice, {
      dimensiones: [...fila.dimensiones, texto],
    })
    setNuevaDimension((prev) => ({ ...prev, [indice]: "" }))
  }

  function eliminarDimension(indiceFila: number, indiceDim: number) {
    const fila = filas[indiceFila]
    if (fila.dimensiones.length <= 1) return
    actualizarFila(indiceFila, {
      dimensiones: fila.dimensiones.filter((_, i) => i !== indiceDim),
    })
  }

  function agregarIndicador(indice: number) {
    const texto = (nuevoIndicador[indice] ?? "").trim()
    if (!texto) return
    const fila = filas[indice]
    if (fila.indicadores.length >= 10) return
    actualizarFila(indice, {
      indicadores: [...fila.indicadores, texto],
    })
    setNuevoIndicador((prev) => ({ ...prev, [indice]: "" }))
  }

  function eliminarIndicador(indiceFila: number, indiceInd: number) {
    const fila = filas[indiceFila]
    if (fila.indicadores.length <= 1) return
    actualizarFila(indiceFila, {
      indicadores: fila.indicadores.filter((_, i) => i !== indiceInd),
    })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="formulario-cabecera">
        <div>
          <h2>Paso P12 · Matriz de Operacionalización de Variables</h2>
          <p>
            Construya la matriz metodológica que descompone cada variable en su
            definición conceptual, definición operacional, dimensiones,
            indicadores empíricos y escala de medición aplicable.
          </p>
        </div>
        <div className="acciones-cabecera">
          <button
            type="button"
            className="boton-primario boton-chico"
            onClick={agregarFila}
            disabled={deshabilitado || filas.length >= 4}
          >
            + Agregar Variable ({filas.length}/4)
          </button>
        </div>
      </div>

      <div className="contenedor-tabla-matriz">
        <table className="tabla-operacionalizacion">
          <thead>
            <tr>
              <th style={{ width: "22%" }}>Variable y Escala</th>
              <th style={{ width: "38%" }}>
                Definición Conceptual y Operacional
              </th>
              <th style={{ width: "20%" }}>Dimensiones (1-6)</th>
              <th style={{ width: "20%" }}>Indicadores (1-10)</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila, indice) => (
              <tr key={indice} className="fila-operacionalizacion">
                {/* Columna 1: Variable y Escala */}
                <td className="celda-variable">
                  <div className="campo-subencabezado">
                    <span className="numero-variable">
                      Variable #{indice + 1}
                    </span>
                    {filas.length > 1 && (
                      <button
                        type="button"
                        className="boton-eliminar-item"
                        onClick={() => eliminarFila(indice)}
                        disabled={deshabilitado}
                        title="Eliminar variable de la matriz"
                      >
                        ✕
                      </button>
                    )}
                  </div>

                  <input
                    type="text"
                    minLength={3}
                    maxLength={120}
                    value={fila.variable}
                    onChange={(e) =>
                      actualizarFila(indice, { variable: e.target.value })
                    }
                    disabled={deshabilitado}
                    placeholder="Nombre de la variable"
                    required
                  />

                  <div className="grupo-escala-selector">
                    <label>
                      <small>Escala de Medición:</small>
                    </label>
                    <select
                      value={fila.escala_medicion}
                      onChange={(e) =>
                        actualizarFila(indice, {
                          escala_medicion: e.target.value as EscalaMedicion,
                        })
                      }
                      disabled={deshabilitado}
                      required
                    >
                      <option value="" disabled>
                        Selecciona una escala
                      </option>
                      {ESCALAS_MEDICION.map((esc) => (
                        <option key={esc.valor} value={esc.valor}>
                          {esc.etiqueta} ({esc.valor})
                        </option>
                      ))}
                    </select>
                  </div>
                </td>

                {/* Columna 2: Definiciones */}
                <td className="celda-definiciones">
                  <div className="subcampo-def">
                    <div className="campo-encabezado">
                      <label>
                        <small>Definición Conceptual (20 a 400 car.):</small>
                      </label>
                      <span className="contador-caracteres">
                        {fila.definicion_conceptual.length} / 400
                      </span>
                    </div>
                    <textarea
                      rows={2}
                      minLength={20}
                      maxLength={400}
                      value={fila.definicion_conceptual}
                      onChange={(e) =>
                        actualizarFila(indice, {
                          definicion_conceptual: e.target.value,
                        })
                      }
                      disabled={deshabilitado}
                      placeholder="Concepto según autores o marco teórico..."
                      required
                    />
                  </div>

                  <div className="subcampo-def">
                    <div className="campo-encabezado">
                      <label>
                        <small>Definición Operacional (20 a 400 car.):</small>
                      </label>
                      <span className="contador-caracteres">
                        {fila.definicion_operacional.length} / 400
                      </span>
                    </div>
                    <textarea
                      rows={2}
                      minLength={20}
                      maxLength={400}
                      value={fila.definicion_operacional}
                      onChange={(e) =>
                        actualizarFila(indice, {
                          definicion_operacional: e.target.value,
                        })
                      }
                      disabled={deshabilitado}
                      placeholder="Cómo se medirá u observará en la práctica..."
                      required
                    />
                  </div>
                </td>

                {/* Columna 3: Dimensiones */}
                <td className="celda-etiquetas">
                  <div className="lista-chips-operacionalizacion">
                    {fila.dimensiones.map((dim, iDim) => (
                      <span key={iDim} className="chip-etiqueta chip-dimension">
                        {dim}
                        {fila.dimensiones.length > 1 && (
                          <button
                            type="button"
                            onClick={() => eliminarDimension(indice, iDim)}
                            disabled={deshabilitado}
                            title="Eliminar dimensión"
                          >
                            ×
                          </button>
                        )}
                      </span>
                    ))}
                  </div>

                  {fila.dimensiones.length < 6 && (
                    <div className="mini-input-agregar">
                      <input
                        type="text"
                        placeholder="Nueva dimensión…"
                        value={nuevaDimension[indice] ?? ""}
                        onChange={(e) =>
                          setNuevaDimension((prev) => ({
                            ...prev,
                            [indice]: e.target.value,
                          }))
                        }
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault()
                            agregarDimension(indice)
                          }
                        }}
                        disabled={deshabilitado}
                      />
                      <button
                        type="button"
                        onClick={() => agregarDimension(indice)}
                        disabled={deshabilitado}
                      >
                        +
                      </button>
                    </div>
                  )}
                </td>

                {/* Columna 4: Indicadores */}
                <td className="celda-etiquetas">
                  <div className="lista-chips-operacionalizacion">
                    {fila.indicadores.map((ind, iInd) => (
                      <span key={iInd} className="chip-etiqueta chip-indicador">
                        {ind}
                        {fila.indicadores.length > 1 && (
                          <button
                            type="button"
                            onClick={() => eliminarIndicador(indice, iInd)}
                            disabled={deshabilitado}
                            title="Eliminar indicador"
                          >
                            ×
                          </button>
                        )}
                      </span>
                    ))}
                  </div>

                  {fila.indicadores.length < 10 && (
                    <div className="mini-input-agregar">
                      <input
                        type="text"
                        placeholder="Nuevo indicador…"
                        value={nuevoIndicador[indice] ?? ""}
                        onChange={(e) =>
                          setNuevoIndicador((prev) => ({
                            ...prev,
                            [indice]: e.target.value,
                          }))
                        }
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault()
                            agregarIndicador(indice)
                          }
                        }}
                        disabled={deshabilitado}
                      />
                      <button
                        type="button"
                        onClick={() => agregarIndicador(indice)}
                        disabled={deshabilitado}
                      >
                        +
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
