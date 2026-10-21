import { type FormEvent, type ReactNode } from "react"
import { Bold, Italic, List, Redo2, Save, Undo2 } from "lucide-react"
import type {
  DatosSalidaPaso,
  EstadoPaso,
  EstadoProyecto,
  PasoCatalogo,
  SalidaP01,
  SalidaP02,
  SalidaP03,
  SalidaP04,
  SalidaP05,
  SalidaP06,
  SalidaP07,
  SalidaP08,
  SalidaP09,
  SalidaP10,
  SalidaP11,
  SalidaP12,
} from "../../../lib/api/cliente"
import AvisosEstado from "./AvisosEstado"
import CabeceraPaso from "./CabeceraPaso"
import EditorContenidoNarrativo from "./EditorContenidoNarrativo"
import FormularioP01 from "./FormularioP01"
import FormularioP02 from "./FormularioP02"
import FormularioP03 from "./FormularioP03"
import FormularioP04 from "./FormularioP04"
import FormularioP05 from "./FormularioP05"
import FormularioP06 from "./FormularioP06"
import FormularioP07 from "./FormularioP07"
import FormularioP08 from "./FormularioP08"
import FormularioP09 from "./FormularioP09"
import FormularioP10 from "./FormularioP10"
import FormularioP11 from "./FormularioP11"
import FormularioP12 from "./FormularioP12"
import PanelAsistenteProximamente from "./PanelAsistenteProximamente"

interface EspacioTrabajoPasoProps {
  codigoPaso: string
  pasoCatalogo?: PasoCatalogo
  estadoPaso?: EstadoPaso
  proyecto: EstadoProyecto
  contenido: string
  alCambiarContenido: (nuevoContenido: string) => void
  datosSalida: DatosSalidaPaso
  alCambiarDatosSalida: (nuevosDatos: DatosSalidaPaso) => void
  guardando: boolean
  cargandoProyecto: boolean
  error: string
  conflicto: string
  confirmacion: string
  alGuardar: (evento: FormEvent) => void
  alRecargar: () => void
  navegacion?: ReactNode
}

export default function EspacioTrabajoPaso({
  codigoPaso,
  pasoCatalogo,
  estadoPaso,
  proyecto,
  contenido,
  alCambiarContenido,
  datosSalida,
  alCambiarDatosSalida,
  guardando,
  cargandoProyecto,
  error,
  conflicto,
  confirmacion,
  alGuardar,
  alRecargar,
  navegacion,
}: EspacioTrabajoPasoProps) {
  const estaBloqueado = estadoPaso?.estado === "BLOQUEADO"
  const deshabilitado = estaBloqueado || guardando || cargandoProyecto

  function renderizarFormularioEspecifico() {
    switch (codigoPaso) {
      case "P01":
        return (
          <FormularioP01
            datos={datosSalida as SalidaP01}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P02":
        return (
          <FormularioP02
            datos={datosSalida as SalidaP02}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P03":
        return (
          <FormularioP03
            datos={datosSalida as SalidaP03}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P04":
        return (
          <FormularioP04
            datos={datosSalida as SalidaP04}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P05":
        return (
          <FormularioP05
            datos={datosSalida as SalidaP05}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
            contenidoNarrativo={contenido}
            alSincronizarNarrativo={alCambiarContenido}
          />
        )
      case "P06":
        return (
          <FormularioP06
            datos={datosSalida as SalidaP06}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P07":
        return (
          <FormularioP07
            datos={datosSalida as SalidaP07}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P08":
        return (
          <FormularioP08
            datos={datosSalida as SalidaP08}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P09":
        return (
          <FormularioP09
            datos={datosSalida as SalidaP09}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P10":
        return (
          <FormularioP10
            datos={datosSalida as SalidaP10}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P11":
        return (
          <FormularioP11
            datos={datosSalida as SalidaP11}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      case "P12":
        return (
          <FormularioP12
            datos={datosSalida as SalidaP12}
            alCambiarDatos={alCambiarDatosSalida}
            deshabilitado={deshabilitado}
          />
        )
      default:
        return (
          <section className="tarjeta-formulario">
            <h2>Paso {codigoPaso}</h2>
            <p>Este paso se conectará en el siguiente capítulo metodológico.</p>
          </section>
        )
    }
  }

  return (
    <form className="editor-page" onSubmit={alGuardar}>
      <div className="editor-titlebar">
        <div>
          <b>{proyecto.titulo || proyecto.nombre}</b>
          <span>
            {codigoPaso} · {pasoCatalogo?.nombre ?? "Paso metodológico"}
          </span>
        </div>
        <span className="document-status">
          Versión {proyecto.version_estado} · Guardado manual
        </span>
      </div>

      <div className="editor-toolbar" aria-label="Barra del editor">
        <select
          disabled
          aria-label="Estilo de texto"
          title="Formato enriquecido: próximamente"
        >
          <option>Texto normal</option>
        </select>
        <button
          type="button"
          disabled
          aria-label="Deshacer"
          title="Próximamente"
        >
          <Undo2 size={14} />
        </button>
        <button
          type="button"
          disabled
          aria-label="Rehacer"
          title="Próximamente"
        >
          <Redo2 size={14} />
        </button>
        <span className="toolbar-divider" />
        <button
          type="button"
          disabled
          aria-label="Negrita"
          title="Próximamente"
        >
          <Bold size={14} />
        </button>
        <button
          type="button"
          disabled
          aria-label="Cursiva"
          title="Próximamente"
        >
          <Italic size={14} />
        </button>
        <button type="button" disabled aria-label="Lista" title="Próximamente">
          <List size={14} />
        </button>
        <span className="toolbar-divider" />
        <span className="toolbar-mode">Edición Markdown</span>
        <button
          className="button button-primary toolbar-save"
          type="submit"
          disabled={deshabilitado}
        >
          <Save size={13} />
          {guardando ? "Guardando…" : `Guardar ${codigoPaso}`}
        </button>
      </div>

      <div className="editor-workspace">
        <aside className="editor-left">{navegacion}</aside>

        <main className="metodologia-document-area">
          <article className="metodologia-paper">
            <CabeceraPaso
              codigoPaso={codigoPaso}
              pasoCatalogo={pasoCatalogo}
              estadoPaso={estadoPaso}
            />

            <AvisosEstado
              error={error}
              conflicto={conflicto}
              confirmacion={confirmacion}
              alRecargar={alRecargar}
            />

            {estaBloqueado && (
              <div className="aviso aviso-bloqueado" role="status">
                <span>
                  🔒 <strong>Paso bloqueado:</strong> Completa las dependencias
                  previas (
                  {(
                    estadoPaso?.dependencias ??
                    pasoCatalogo?.dependencias ??
                    []
                  ).join(", ") || "paso anterior"}
                  ) para habilitar la edición y guardado.
                </span>
              </div>
            )}

            <div className="documento-secciones">
              <EditorContenidoNarrativo
                contenido={contenido}
                alCambiarContenido={alCambiarContenido}
                deshabilitado={deshabilitado}
              />

              {renderizarFormularioEspecifico()}
            </div>
          </article>
        </main>

        <aside className="editor-right">
          <div className="panel-tabs right-tabs">
            <button className="active" type="button">
              Asistente
            </button>
            <button type="button" disabled>
              Comentarios
            </button>
          </div>

          <div className="context-strip">
            <span>
              <b>Contexto actual: {codigoPaso}</b>
              <small>{pasoCatalogo?.nombre ?? "Paso metodológico"}</small>
            </span>
          </div>

          <div className="panel-lateral-contenido">
            <section className="resumen-guardado">
              <span className="eyebrow blue">CONTROL DE VERSIÓN</span>
              <h2>Guardado seguro</h2>
              <ul>
                <li>Versión esperada: {proyecto.version_estado}</li>
                <li>UUID nuevo en cada intento de guardado.</li>
                <li>Los conflictos nunca sobrescriben datos.</li>
                {estaBloqueado && (
                  <li className="texto-error">
                    Completa las dependencias antes de guardar.
                  </li>
                )}
              </ul>
              <button
                className="button button-primary boton-guardar"
                type="submit"
                disabled={deshabilitado}
              >
                <Save size={13} />
                {guardando
                  ? "Guardando…"
                  : estaBloqueado
                    ? `Bloqueado (${codigoPaso})`
                    : `Guardar ${codigoPaso}`}
              </button>
            </section>

            <PanelAsistenteProximamente />
          </div>
        </aside>
      </div>
    </form>
  )
}
