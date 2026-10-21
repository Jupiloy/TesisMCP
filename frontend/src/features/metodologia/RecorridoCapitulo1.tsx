import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react"
import {
  api,
  ErrorApi,
  type DatosSalidaPaso,
  type EstadoProyecto,
  type PasoCatalogo,
  type ResumenProyecto,
  type UsuarioSesion,
} from "../../lib/api/cliente"
import EspacioTrabajoPaso from "./componentes/EspacioTrabajoPaso"
import { salidaP01Inicial } from "./componentes/FormularioP01"
import { salidaP02Inicial } from "./componentes/FormularioP02"
import { salidaP03Inicial } from "./componentes/FormularioP03"
import { salidaP04Inicial } from "./componentes/FormularioP04"
import { salidaP05Inicial } from "./componentes/FormularioP05"

const CODIGOS_CAPITULO_1 = ["P01", "P02", "P03", "P04", "P05"] as const
type CodigoPasoCap1 = (typeof CODIGOS_CAPITULO_1)[number]

const etiquetasEstado = {
  COMPLETADO: "Completado",
  DISPONIBLE: "Disponible",
  BLOQUEADO: "Bloqueado",
} as const

function obtenerSalidaInicial(codigoPaso: string): DatosSalidaPaso {
  switch (codigoPaso) {
    case "P01":
      return salidaP01Inicial()
    case "P02":
      return salidaP02Inicial()
    case "P03":
      return salidaP03Inicial()
    case "P04":
      return salidaP04Inicial()
    case "P05":
      return salidaP05Inicial()
    default:
      return {}
  }
}

function mensajeError(error: unknown): string {
  if (error instanceof ErrorApi) {
    return `${error.codigo}: ${error.message} — ${error.detalle}`
  }
  return error instanceof Error ? error.message : "Ocurrió un error inesperado."
}

export default function RecorridoCapitulo1() {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null)
  const [catalogo, setCatalogo] = useState<PasoCatalogo[]>([])
  const [proyectos, setProyectos] = useState<ResumenProyecto[]>([])
  const [proyecto, setProyecto] = useState<EstadoProyecto | null>(null)
  const [codigoPasoActivo, setCodigoPasoActivo] = useState<CodigoPasoCap1>("P01")
  const [contenido, setContenido] = useState("")
  const [datosSalida, setDatosSalida] = useState<DatosSalidaPaso>(salidaP01Inicial)

  const [cargando, setCargando] = useState(true)
  const [cargandoProyecto, setCargandoProyecto] = useState(false)
  const [creando, setCreando] = useState(false)
  const [guardando, setGuardando] = useState(false)
  const [sinSesion, setSinSesion] = useState(false)
  const [error, setError] = useState("")
  const [conflicto, setConflicto] = useState("")
  const [confirmacion, setConfirmacion] = useState("")
  const [nombreNuevo, setNombreNuevo] = useState("")
  const [tituloNuevo, setTituloNuevo] = useState("")

  const hidratarFormularioPaso = useCallback(
    (estado: EstadoProyecto, codigoPaso: string) => {
      const paso = estado.pasos.find((p) => p.codigo === codigoPaso)
      setContenido(paso?.contenido_md ?? "")
      if (paso?.datos_salida && Object.keys(paso.datos_salida).length > 0) {
        setDatosSalida(paso.datos_salida)
      } else {
        setDatosSalida(obtenerSalidaInicial(codigoPaso))
      }
    },
    [],
  )

  const abrirProyecto = useCallback(
    async (idProyecto: string, pasoDeseado?: CodigoPasoCap1) => {
      if (!idProyecto) return
      setCargandoProyecto(true)
      setError("")
      setConflicto("")
      setConfirmacion("")
      try {
        const estado = await api.consultarProyecto(idProyecto)
        setProyecto(estado)
        const pasoASeleccionar = pasoDeseado ?? codigoPasoActivo
        hidratarFormularioPaso(estado, pasoASeleccionar)
      } catch (errorDesconocido) {
        setError(mensajeError(errorDesconocido))
      } finally {
        setCargandoProyecto(false)
      }
    },
    [codigoPasoActivo, hidratarFormularioPaso],
  )

  const cargarInicial = useCallback(async () => {
    setCargando(true)
    setError("")
    try {
      const sesion = await api.consultarSesion()
      setUsuario(sesion)
      const [pasos, lista] = await Promise.all([
        api.consultarCatalogo(),
        api.listarProyectos(),
      ])
      setCatalogo(pasos)
      setProyectos(lista)
      if (lista.length > 0) {
        await abrirProyecto(lista[0].id_proyecto, "P01")
      }
    } catch (errorDesconocido) {
      if (
        errorDesconocido instanceof ErrorApi &&
        errorDesconocido.estadoHttp === 401
      ) {
        setSinSesion(true)
      } else {
        setError(mensajeError(errorDesconocido))
      }
    } finally {
      setCargando(false)
    }
  }, [abrirProyecto])

  useEffect(() => {
    void cargarInicial()
  }, [cargarInicial])

  // Pasos de Capítulo 1 desde el catálogo real
  const pasosCapitulo1 = useMemo(() => {
    return CODIGOS_CAPITULO_1.map((codigo) => {
      const pasoCat = catalogo.find((p) => p.codigo === codigo)
      const pasoEstado = proyecto?.pasos.find((p) => p.codigo === codigo)
      return {
        codigo,
        catalogo: pasoCat,
        estado: pasoEstado,
      }
    })
  }, [catalogo, proyecto])

  const pasoCatalogoActivo = useMemo(
    () => catalogo.find((p) => p.codigo === codigoPasoActivo),
    [catalogo, codigoPasoActivo],
  )

  const pasoEstadoActivo = useMemo(
    () => proyecto?.pasos.find((p) => p.codigo === codigoPasoActivo),
    [proyecto, codigoPasoActivo],
  )

  function seleccionarPaso(codigo: CodigoPasoCap1) {
    if (codigo === codigoPasoActivo) return
    const pasoEst = proyecto?.pasos.find((p) => p.codigo === codigo)
    // Regla: Abrir únicamente los pasos disponibles o completados según el backend
    if (pasoEst?.estado === "BLOQUEADO") {
      setError(
        `El paso ${codigo} está bloqueado. Completa ${pasoEst.dependencias.join(
          ", ",
        )} antes de continuar.`,
      )
      return
    }
    setError("")
    setConflicto("")
    setConfirmacion("")
    setCodigoPasoActivo(codigo)
    if (proyecto) {
      hidratarFormularioPaso(proyecto, codigo)
    }
  }

  async function crearProyecto(evento: FormEvent) {
    evento.preventDefault()
    setCreando(true)
    setError("")
    try {
      const creado = await api.crearProyecto(nombreNuevo, tituloNuevo)
      setProyectos(await api.listarProyectos())
      setProyecto(creado)
      setCodigoPasoActivo("P01")
      hidratarFormularioPaso(creado, "P01")
      setNombreNuevo("")
      setTituloNuevo("")
      setConfirmacion("Proyecto creado y abierto desde PostgreSQL.")
    } catch (errorDesconocido) {
      setError(mensajeError(errorDesconocido))
    } finally {
      setCreando(false)
    }
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault()
    if (!proyecto) return
    if (pasoEstadoActivo?.estado === "BLOQUEADO") {
      setError(
        `No se puede guardar el paso ${codigoPasoActivo} porque sus prerrequisitos no están completados.`,
      )
      return
    }

    setGuardando(true)
    setError("")
    setConflicto("")
    setConfirmacion("")
    try {
      // 1. Guardar con UUID real y versión optimista recibida
      const claveIdempotencia = crypto.randomUUID()
      await api.guardarPaso(
        proyecto.id_proyecto,
        codigoPasoActivo,
        contenido,
        datosSalida as Record<string, unknown>,
        proyecto.version_estado,
        claveIdempotencia,
      )

      // 2. Volver a consultar el proyecto completo desde PostgreSQL tras el guardado
      const actualizado = await api.consultarProyecto(proyecto.id_proyecto)
      setProyecto(actualizado)

      // 3. Hidratar nuevamente con los datos persistidos
      hidratarFormularioPaso(actualizado, codigoPasoActivo)

      // 4. Mostrar confirmación solo tras comprobar recarga
      setConfirmacion(
        `El paso ${codigoPasoActivo} se guardó y se recargó desde PostgreSQL; el contenido persistió con éxito.`,
      )
      setProyectos(await api.listarProyectos())
    } catch (errorDesconocido) {
      if (
        errorDesconocido instanceof ErrorApi &&
        errorDesconocido.codigo === "CONFLICTO_VERSION"
      ) {
        setConflicto(mensajeError(errorDesconocido))
      } else {
        setError(mensajeError(errorDesconocido))
      }
    } finally {
      setGuardando(false)
    }
  }

  if (cargando) {
    return (
      <div className="estado-pantalla">
        Cargando sesión, proyectos y metodología…
      </div>
    )
  }

  if (sinSesion) {
    return (
      <div className="estado-pantalla">
        <section className="tarjeta-estado">
          <span className="marca-grande">TesisMCP</span>
          <h1>Inicia sesión para continuar</h1>
          <p>Este recorrido usa la sesión segura de Django.</p>
          <a className="button button-primary" href="/admin/login/?next=/">
            Iniciar sesión
          </a>
        </section>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar barra-metodologia">
        <div className="brand">
          <div className="brand-mark">T</div>
          <div>
            <b>TesisMCP</b>
            <span>Capítulo 1: P01 a P05</span>
          </div>
        </div>

        <label className="selector-proyecto">
          Proyecto activo
          <select
            value={proyecto?.id_proyecto ?? ""}
            onChange={(evento) => void abrirProyecto(evento.target.value)}
            disabled={proyectos.length === 0 || cargandoProyecto}
          >
            {proyectos.length === 0 && <option value="">Sin proyectos</option>}
            {proyectos.map((item) => (
              <option key={item.id_proyecto} value={item.id_proyecto}>
                {item.nombre}
              </option>
            ))}
          </select>
        </label>

        <nav className="arbol-pasos" aria-label="Recorrido Capítulo 1">
          <section>
            <h2>Capítulo 1 · Tema y Alcance</h2>
            {pasosCapitulo1.map(({ codigo, catalogo: cat, estado: est }) => {
              const estaActivo = codigo === codigoPasoActivo
              const estado = est?.estado ?? "DISPONIBLE"
              const estaBloqueado = estado === "BLOQUEADO"

              return (
                <button
                  key={codigo}
                  className={`${estaActivo ? "paso-activo" : ""} paso-item-${estado.toLowerCase()}`}
                  type="button"
                  onClick={() => seleccionarPaso(codigo)}
                  disabled={estaBloqueado}
                  title={
                    estaBloqueado
                      ? `Bloqueado: completa ${(est?.dependencias ?? cat?.dependencias ?? []).join(", ") || "paso anterior"}`
                      : cat?.nombre ?? codigo
                  }
                >
                  <span>{codigo}</span>
                  <span>
                    <b>{cat?.nombre ?? codigo}</b>
                    <small>{etiquetasEstado[estado]}</small>
                  </span>
                </button>
              )
            })}
          </section>
        </nav>

        <div className="profile">
          <div className="avatar">
            {usuario?.nombre_visible.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <b>{usuario?.nombre_visible}</b>
            <span>{usuario?.correo}</span>
          </div>
        </div>
      </aside>

      <main className="app-main">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Metodología</span>
            <span>› Capítulo 1</span>
            <strong>
              › {codigoPasoActivo} · {pasoCatalogoActivo?.nombre ?? codigoPasoActivo}
            </strong>
          </div>
          {proyecto && (
            <span className="version-real">
              Versión del estado: {proyecto.version_estado}
            </span>
          )}
        </header>

        {cargandoProyecto && (
          <div className="aviso">Abriendo el proyecto desde PostgreSQL…</div>
        )}

        {error && !proyecto && (
          <div className="pagina-p01">
            <div className="aviso aviso-error" role="alert">
              {error}
            </div>
          </div>
        )}

        {!proyecto ? (
          <div className="pagina-p01">
            <section className="tarjeta-formulario crear-proyecto">
              <span className="eyebrow blue">NUEVO PROYECTO</span>
              <h1>Crea un proyecto para comenzar la metodología</h1>
              <p>No se encontraron proyectos propios para la sesión actual.</p>
              <form onSubmit={crearProyecto}>
                <label>
                  Nombre del proyecto
                  <input
                    required
                    maxLength={160}
                    value={nombreNuevo}
                    onChange={(evento) => setNombreNuevo(evento.target.value)}
                  />
                </label>
                <label>
                  Título provisional
                  <input
                    maxLength={300}
                    value={tituloNuevo}
                    onChange={(evento) => setTituloNuevo(evento.target.value)}
                  />
                </label>
                <button
                  className="button button-primary"
                  type="submit"
                  disabled={creando}
                >
                  {creando ? "Creando…" : "Crear proyecto"}
                </button>
              </form>
            </section>
          </div>
        ) : (
          <EspacioTrabajoPaso
            codigoPaso={codigoPasoActivo}
            pasoCatalogo={pasoCatalogoActivo}
            estadoPaso={pasoEstadoActivo}
            proyecto={proyecto}
            contenido={contenido}
            alCambiarContenido={setContenido}
            datosSalida={datosSalida}
            alCambiarDatosSalida={setDatosSalida}
            guardando={guardando}
            cargandoProyecto={cargandoProyecto}
            error={error}
            conflicto={conflicto}
            confirmacion={confirmacion}
            alGuardar={guardar}
            alRecargar={() => void abrirProyecto(proyecto.id_proyecto)}
          />
        )}
      </main>
    </div>
  )
}
