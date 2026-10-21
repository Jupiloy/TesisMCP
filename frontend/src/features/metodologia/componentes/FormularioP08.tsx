import type { SalidaP08 } from "../../../lib/api/cliente"

export const salidaP08Inicial = (): SalidaP08 => ({
  brecha_detectada: "",
  aporte_propuesto: "",
  estado_evidencia: "EVIDENCIA_PENDIENTE",
})

interface FormularioP08Props {
  datos: SalidaP08
  alCambiarDatos: (nuevosDatos: SalidaP08) => void
  deshabilitado?: boolean
}

export default function FormularioP08({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP08Props) {
  const brechaValida =
    datos.brecha_detectada.trim().length >= 30 &&
    datos.brecha_detectada.trim().length <= 400

  const aporteValido =
    datos.aporte_propuesto.trim().length >= 30 &&
    datos.aporte_propuesto.trim().length <= 400

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P08: Originalidad y aporte</h2>
          <p>
            Explicar la contribución novedosa de la tesis frente a la literatura
            previa y documentar la brecha de conocimiento identificada.
          </p>
        </div>
      </div>

      <div className="lista-temas">
        {/* Brecha Detectada */}
        <label className="campo-ancho">
          <span className="eyebrow amber">1. BRECHA DE INVESTIGACIÓN DETECTADA (30 a 400 caracteres)</span>
          <textarea
            required
            minLength={30}
            maxLength={400}
            value={datos.brecha_detectada}
            onChange={(e) =>
              alCambiarDatos({ ...datos, brecha_detectada: e.target.value })
            }
            disabled={deshabilitado}
            placeholder="Describe qué aspecto específico no ha sido resuelto o explorado suficientemente por los antecedentes previos…"
            rows={4}
          />
          <div className="indicadores-pregunta">
            <span
              className={`tag-componente ${
                brechaValida ? "valido" : "pendiente"
              }`}
            >
              {brechaValida ? "✓ Longitud válida" : "○ Mínimo 30 caracteres"}
            </span>
            <span className="caracteres-ayuda">
              {datos.brecha_detectada.length} / 400 caracteres
            </span>
          </div>
        </label>

        {/* Aporte Propuesto */}
        <label className="campo-ancho">
          <span className="eyebrow blue">2. APORTE NOVEDOSO PROPUESTO (30 a 400 caracteres)</span>
          <textarea
            required
            minLength={30}
            maxLength={400}
            value={datos.aporte_propuesto}
            onChange={(e) =>
              alCambiarDatos({ ...datos, aporte_propuesto: e.target.value })
            }
            disabled={deshabilitado}
            placeholder="Especifica el artefacto, modelo, algoritmo o solución metodológica que esta tesis introduce para cerrar la brecha…"
            rows={4}
          />
          <div className="indicadores-pregunta">
            <span
              className={`tag-componente ${
                aporteValido ? "valido" : "pendiente"
              }`}
            >
              {aporteValido ? "✓ Longitud válida" : "○ Mínimo 30 caracteres"}
            </span>
            <span className="caracteres-ayuda">
              {datos.aporte_propuesto.length} / 400 caracteres
            </span>
          </div>
        </label>

        {/* Estado de Evidencia Fijado por Contrato */}
        <div className="tarjeta-estado-evidencia">
          <div className="icono-evidencia">📎</div>
          <div>
            <strong>Estado de Evidencia Documental</strong>
            <p>
              Fijado formalmente por el contrato P08 como{" "}
              <code>EVIDENCIA_PENDIENTE</code>. Las evidencias ancladas a páginas
              físicas de artículos y tesis se vincularán en los módulos de revisión
              y literatura.
            </p>
          </div>
          <span className="status status-warning">EVIDENCIA_PENDIENTE</span>
        </div>
      </div>
    </section>
  )
}
