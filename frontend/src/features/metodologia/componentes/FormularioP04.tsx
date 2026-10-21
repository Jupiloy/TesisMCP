import type { SalidaP04 } from "../../../lib/api/cliente"

const contarPalabras = (texto: string): number =>
  texto.trim().split(/\s+/).filter(Boolean).length

export const salidaP04Inicial = (): SalidaP04 => ({
  titulo_oficial: "",
  conteo_palabras: 0,
  variables_confirmadas: [""],
  unidad_analisis_confirmada: "",
  lugar_confirmado: "",
  periodo_confirmado: 2026,
})

export function normalizarSalidaP04(
  datos?: Partial<SalidaP04> | null,
): SalidaP04 {
  const base = salidaP04Inicial()
  if (!datos) return base
  return {
    titulo_oficial: datos.titulo_oficial ?? base.titulo_oficial,
    conteo_palabras:
      typeof datos.conteo_palabras === "number"
        ? datos.conteo_palabras
        : contarPalabras(datos.titulo_oficial ?? ""),
    variables_confirmadas:
      Array.isArray(datos.variables_confirmadas) &&
      datos.variables_confirmadas.length > 0
        ? datos.variables_confirmadas
        : base.variables_confirmadas,
    unidad_analisis_confirmada:
      datos.unidad_analisis_confirmada ?? base.unidad_analisis_confirmada,
    lugar_confirmado: datos.lugar_confirmado ?? base.lugar_confirmado,
    periodo_confirmado:
      typeof datos.periodo_confirmado === "number"
        ? datos.periodo_confirmado
        : base.periodo_confirmado,
  }
}

interface FormularioP04Props {
  datos: SalidaP04
  alCambiarDatos: (nuevosDatos: SalidaP04) => void
  deshabilitado?: boolean
}

export default function FormularioP04({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP04Props) {
  const datosSeguros = normalizarSalidaP04(datos)

  function actualizarTitulo(nuevoTitulo: string) {
    const palabras = contarPalabras(nuevoTitulo)
    alCambiarDatos({
      ...datosSeguros,
      titulo_oficial: nuevoTitulo,
      conteo_palabras: palabras,
    })
  }

  function actualizarVariable(indice: number, valor: string) {
    const nuevasVariables = [...datosSeguros.variables_confirmadas]
    nuevasVariables[indice] = valor
    alCambiarDatos({
      ...datosSeguros,
      variables_confirmadas: nuevasVariables,
    })
  }

  function agregarVariable() {
    if (datosSeguros.variables_confirmadas.length >= 2) return
    alCambiarDatos({
      ...datosSeguros,
      variables_confirmadas: [...datosSeguros.variables_confirmadas, ""],
    })
  }

  function quitarVariable(indice: number) {
    if (datosSeguros.variables_confirmadas.length <= 1) return
    alCambiarDatos({
      ...datosSeguros,
      variables_confirmadas: datosSeguros.variables_confirmadas.filter((_, i) => i !== indice),
    })
  }

  // Verificación reactiva de inclusión de subcadenas en el título
  const tituloMinusculas = datosSeguros.titulo_oficial.toLowerCase()
  const componentesVerificados = {
    variables: datosSeguros.variables_confirmadas.map((v) => ({
      nombre: v,
      presente: v.trim().length > 0 && tituloMinusculas.includes(v.trim().toLowerCase()),
    })),
    unidad: {
      valor: datosSeguros.unidad_analisis_confirmada,
      presente:
        datosSeguros.unidad_analisis_confirmada.trim().length >= 3 &&
        tituloMinusculas.includes(datosSeguros.unidad_analisis_confirmada.trim().toLowerCase()),
    },
    lugar: {
      valor: datosSeguros.lugar_confirmado,
      presente:
        datosSeguros.lugar_confirmado.trim().length >= 3 &&
        tituloMinusculas.includes(datosSeguros.lugar_confirmado.trim().toLowerCase()),
    },
    periodo: {
      valor: datosSeguros.periodo_confirmado,
      presente: tituloMinusculas.includes(String(datosSeguros.periodo_confirmado)),
    },
  }

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P04: Delimitación final y título</h2>
          <p>
            Formular el título oficial de máximo 20 palabras. Debe contener
            literalmente las variables, la unidad de análisis, el lugar y el periodo.
          </p>
        </div>
      </div>

      <div className="lista-temas">
        <label className="campo-ancho">
          Título oficial de la tesis (15 a 250 caracteres, máximo 20 palabras)
          <input
            required
            minLength={15}
            maxLength={250}
            value={datosSeguros.titulo_oficial}
            onChange={(e) => actualizarTitulo(e.target.value)}
            disabled={deshabilitado}
            placeholder="Ejemplo: Protocolo MCP y Circuito Determinista en la Formulación de Tesis de Ingeniería en Piura 2026"
          />
          <div className="indicadores-titulo">
            <span
              className={`badge-contador ${
                datosSeguros.conteo_palabras > 20 || datosSeguros.conteo_palabras === 0
                  ? "texto-error"
                  : "texto-ok"
              }`}
            >
              Palabras: {datosSeguros.conteo_palabras} / 20 máx.
            </span>
            <span className="caracteres-ayuda">
              {datosSeguros.titulo_oficial.length} / 250 caracteres (mínimo 15)
            </span>
          </div>
        </label>

        {/* Verificación de subcadenas obligatorias */}
        <div className="panel-checklist-titulo">
          <small className="eyebrow">REGLA DE ORO DE INCLUSIÓN LITERAL</small>
          <div className="items-checklist">
            {componentesVerificados.variables.map((item, idx) => (
              <span
                key={idx}
                className={`tag-componente ${item.presente ? "valido" : "pendiente"}`}
              >
                {item.presente ? "✓" : "○"} Variable {idx + 1}:{" "}
                {item.nombre || "(vacía)"}
              </span>
            ))}
            <span
              className={`tag-componente ${
                componentesVerificados.unidad.presente ? "valido" : "pendiente"
              }`}
            >
              {componentesVerificados.unidad.presente ? "✓" : "○"} Unidad:{" "}
              {componentesVerificados.unidad.valor || "(vacía)"}
            </span>
            <span
              className={`tag-componente ${
                componentesVerificados.lugar.presente ? "valido" : "pendiente"
              }`}
            >
              {componentesVerificados.lugar.presente ? "✓" : "○"} Lugar:{" "}
              {componentesVerificados.lugar.valor || "(vacío)"}
            </span>
            <span
              className={`tag-componente ${
                componentesVerificados.periodo.presente ? "valido" : "pendiente"
              }`}
            >
              {componentesVerificados.periodo.presente ? "✓" : "○"} Periodo:{" "}
              {componentesVerificados.periodo.valor}
            </span>
          </div>
        </div>

        <div className="campo-ancho">
          <div className="titulo-seccion-variables">
            <label className="label-sin-margen">
              Variables confirmadas (1 a 2 variables)
            </label>
            <button
              type="button"
              className="button button-secondary boton-agregar-pequeno"
              onClick={agregarVariable}
              disabled={deshabilitado || datosSeguros.variables_confirmadas.length >= 2}
            >
              + Agregar variable
            </button>
          </div>
          <div className="lista-variables-inputs">
            {datosSeguros.variables_confirmadas.map((variable, idx) => (
              <div key={idx} className="fila-variable">
                <input
                  required
                  value={variable}
                  onChange={(e) => actualizarVariable(idx, e.target.value)}
                  disabled={deshabilitado}
                  placeholder={`Variable ${idx + 1} (ej. Protocolo MCP)`}
                />
                <button
                  type="button"
                  className="quitar-tema"
                  onClick={() => quitarVariable(idx)}
                  disabled={deshabilitado || datosSeguros.variables_confirmadas.length <= 1}
                >
                  Quitar
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="fila-tres-columnas">
          <label>
            Unidad de análisis (mínimo 3 caracteres)
            <input
              required
              minLength={3}
              value={datosSeguros.unidad_analisis_confirmada}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  unidad_analisis_confirmada: e.target.value,
                })
              }
              disabled={deshabilitado}
              placeholder="Ej. Tesis de Ingeniería"
            />
          </label>

          <label>
            Contexto espacial / Lugar (mínimo 3 caracteres)
            <input
              required
              minLength={3}
              value={datosSeguros.lugar_confirmado}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  lugar_confirmado: e.target.value,
                })
              }
              disabled={deshabilitado}
              placeholder="Ej. Piura"
            />
          </label>

          <label>
            Periodo temporal (2024 a 2030)
            <input
              type="number"
              min={2024}
              max={2030}
              required
              value={datosSeguros.periodo_confirmado}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  periodo_confirmado: Number(e.target.value),
                })
              }
              disabled={deshabilitado}
            />
          </label>
        </div>
      </div>
    </section>
  )
}
