import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react"
import {
  BookOpenText,
  FileText,
  LayoutDashboard,
  Library,
  MessageSquareText,
} from "lucide-react"
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
import NavegacionMetodologia from "./componentes/NavegacionMetodologia"
import { salidaP01Inicial } from "./componentes/FormularioP01"
import { salidaP02Inicial } from "./componentes/FormularioP02"
import { salidaP03Inicial } from "./componentes/FormularioP03"
import { salidaP04Inicial } from "./componentes/FormularioP04"
import { salidaP05Inicial } from "./componentes/FormularioP05"
import { salidaP06Inicial } from "./componentes/FormularioP06"
import { salidaP07Inicial } from "./componentes/FormularioP07"
import { salidaP08Inicial } from "./componentes/FormularioP08"
import { salidaP09Inicial } from "./componentes/FormularioP09"
import { salidaP10Inicial } from "./componentes/FormularioP10"
import { salidaP11Inicial } from "./componentes/FormularioP11"
import { salidaP12Inicial } from "./componentes/FormularioP12"

const CAPITULOS_CONFIG = [
  {
    numero: 1,
    titulo: "Capítulo 1 · Tema y Alcance",
    codigos: ["P01", "P02", "P03", "P04", "P05"] as const,
  },
  {
    numero: 2,
    titulo: "Capítulo 2 · Problema y Justificación",
    codigos: ["P06", "P07", "P08"] as const,
  },
  {
    numero: 3,
    titulo: "Capítulo 3 · Objetivos e Hipótesis",
    codigos: ["P09", "P10", "P11", "P12"] as const,
  },
] as const

type CodigoPasoMetodologia = typeof CAPITULOS_CONFIG[0]["codigos"][number] | typeof CAPITULOS_CONFIG[1]["codigos"][number] | typeof CAPITULOS_CONFIG[2]["codigos"][number]

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
    case "P06":
      return salidaP06Inicial()
    case "P07":
      return salidaP07Inicial()
    case "P08":
      return salidaP08Inicial()
    case "P09":
      return salidaP09Inicial()
    case "P10":
      return salidaP10Inicial()
    case "P11":
      return salidaP11Inicial()
    case "P12":
      return salidaP12Inicial()
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

export default function RecorridoCapitulos() {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null)
  const [catalogo, setCatalogo] = useState<PasoCatalogo[]>([])
  const [proyectos, setProyectos] = useState<ResumenProyecto[]>([])
  const [proyecto, setProyecto] = useState<EstadoProyecto | null>(null)
  const [codigoPasoActivo, setCodigoPasoActivo] =
    useState<CodigoPasoMetodologia>("P01")
  const [capitulosAbiertos, setCapitulosAbiertos] = useState<number[]>([
    1, 2, 3,
  ])
  const [contenido, setContenido] = useState("")
  const [datosSalida, setDatosSalida] =
    useState<DatosSalidaPaso>(salidaP01Inicial)

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
    async (idProyecto: string, pasoDeseado: CodigoPasoMetodologia = "P01") => {
      if (!idProyecto) return
      setCargandoProyecto(true)
      setError("")
      setConflicto("")
      setConfirmacion("")
      try {
        const estado = await api.consultarProyecto(idProyecto)
        setProyecto(estado)
        setCodigoPasoActivo(pasoDeseado)
        hidratarFormularioPaso(estado, pasoDeseado)
      } catch (errorDesconocido) {
        setError(mensajeError(errorDesconocido))
      } finally {
        setCargandoProyecto(false)
      }
    },
    [hidratarFormularioPaso],
  )

  const cargarInicial = useCallback(async () => {
    setCargando(true)
    setError("")
    setSinSesion(false)
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

  function conmutarCapitulo(numeroCapitulo: number) {
    setCapitulosAbiertos((actuales) =>
      actuales.includes(numeroCapitulo)
        ? actuales.filter((n) => n !== numeroCapitulo)
        : [...actuales, numeroCapitulo],
    )
  }

  function seleccionarPaso(codigo: CodigoPasoMetodologia) {
    if (codigo === codigoPasoActivo) return
    const pasoEst = proyecto?.pasos.find((p) => p.codigo === codigo)
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

  const pasoCatalogoActivo = useMemo(
    () => catalogo.find((p) => p.codigo === codigoPasoActivo),
    [catalogo, codigoPasoActivo],
  )

  const pasoEstadoActivo = useMemo(
    () => proyecto?.pasos.find((p) => p.codigo === codigoPasoActivo),
    [proyecto, codigoPasoActivo],
  )

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
        `No se puede guardar el paso ${codigoPasoActivo} porque sus dependencias están bloqueadas.`,
      )
      return
    }

    setGuardando(true)
    setError("")
    setConflicto("")
    setConfirmacion("")
    try {
      // 1. Guardar con clave de idempotencia UUID v4 y version_esperada
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
        Cargando sesión, proyectos y catálogo metodológico…
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
            <span>Capítulos 1, 2 y 3</span>
          </div>
        </div>

        <nav className="main-nav" aria-label="Navegación principal">
          <button className="nav-item" type="button" disabled>
            <LayoutDashboard size={16} aria-hidden="true" />
            <span>Panel principal</span>
            <small className="nav-soon">Próximamente</small>
          </button>
          <button className="nav-item active" type="button" aria-current="page">
            <BookOpenText size={16} aria-hidden="true" />
            <span>Metodología</span>
          </button>
          <button className="nav-item" type="button" disabled>
            <Library size={16} aria-hidden="true" />
            <span>Biblioteca</span>
            <small className="nav-soon">Próximamente</small>
          </button>
          <button className="nav-item" type="button" disabled>
            <MessageSquareText size={16} aria-hidden="true" />
            <span>Revisión</span>
            <small className="nav-soon">Próximamente</small>
          </button>
        </nav>

        <label className="selector-proyecto">
          Proyecto activo
          <select
            value={proyecto?.id_proyecto ?? ""}
            onChange={(evento) => void abrirProyecto(evento.target.value)}
            disabled={proyectos.length === 0 || cargandoProyecto}
          >
            {proyectos.length === 0 && (
              <option value="">
                {error ? "No disponible" : "Sin proyectos"}
              </option>
            )}
            {proyectos.map((item) => (
              <option key={item.id_proyecto} value={item.id_proyecto}>
                {item.nombre}
              </option>
            ))}
          </select>
        </label>

        <section className="sidebar-project">
          <span className="eyebrow">PROYECTO ACTIVO</span>
          <strong>
            {proyecto?.titulo || proyecto?.nombre || "Sin proyecto disponible"}
          </strong>
          <span>
            {proyecto
              ? `Versión ${proyecto.version_estado} · ${proyecto.pasos.filter((paso) => paso.estado === "COMPLETADO").length}/${proyecto.pasos.length} pasos`
              : "Conecta el backend para continuar"}
          </span>
        </section>

        <div className="sidebar-bottom">
          <span
            className="download-project descarga-proximamente"
            aria-disabled="true"
          >
            <FileText size={15} aria-hidden="true" />
            Exportar documento
            <small>Próximamente</small>
          </span>

          {usuario && (
            <div className="profile">
              <div className="avatar">
                {usuario.nombre_visible.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <b>{usuario.nombre_visible}</b>
                <span>{usuario.correo}</span>
              </div>
            </div>
          )}
        </div>
      </aside>

      <main className="app-main">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Metodología</span>
            <strong>
              › {codigoPasoActivo} ·{" "}
              {pasoCatalogoActivo?.nombre ?? codigoPasoActivo}
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

        {!proyecto ? (
          <div className="pagina-p01">
            {error ? (
              <section
                className="tarjeta-formulario crear-proyecto"
                role="alert"
              >
                <span className="eyebrow amber">CONEXIÓN NO DISPONIBLE</span>
                <h1>No fue posible cargar los datos del proyecto</h1>
                <p className="aviso aviso-error">{error}</p>
                <button
                  className="button button-primary"
                  type="button"
                  onClick={() => void cargarInicial()}
                >
                  Reintentar conexión
                </button>
              </section>
            ) : (
              <section className="tarjeta-formulario crear-proyecto">
                <span className="eyebrow blue">NUEVO PROYECTO</span>
                <h1>Crea un proyecto para comenzar la metodología</h1>
                <p>
                  No se encontraron proyectos propios para la sesión actual.
                </p>
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
            )}
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
            alRecargar={() =>
              void abrirProyecto(proyecto.id_proyecto, codigoPasoActivo)
            }
            navegacion={
              <NavegacionMetodologia
                capitulos={CAPITULOS_CONFIG}
                capitulosAbiertos={capitulosAbiertos}
                catalogo={catalogo}
                proyecto={proyecto}
                codigoPasoActivo={codigoPasoActivo}
                alConmutarCapitulo={conmutarCapitulo}
                alSeleccionarPaso={(codigo) =>
                  seleccionarPaso(codigo as CodigoPasoMetodologia)
                }
              />
            }
          />
        )}
      </main>
    </div>
  )
}
