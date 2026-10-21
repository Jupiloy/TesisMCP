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
  type EstadoProyecto,
  type PasoCatalogo,
  type ResumenProyecto,
  type SalidaP01,
  type TemaCandidato,
  type UsuarioSesion,
} from "../../lib/api/cliente"

const crearTemaVacio = (id: number): TemaCandidato => ({
  id,
  titulo_tentativo: "",
  pros: [""],
  contras: [""],
  viabilidad_preliminar: "MEDIA",
})

const salidaInicial = (): SalidaP01 => ({
  temas_propuestos: Array.from({ length: 5 }, (_, indice) =>
    crearTemaVacio(indice + 1),
  ),
  tema_preseleccionado_id: null,
})

const etiquetasEstado = {
  COMPLETADO: "Completado",
  DISPONIBLE: "Disponible",
  BLOQUEADO: "Bloqueado",
} as const

function mensajeError(error: unknown): string {
  if (error instanceof ErrorApi)
    return `${error.codigo}: ${error.message} — ${error.detalle}`
  return error instanceof Error ? error.message : "Ocurrió un error inesperado."
}

const separarLineas = (texto: string) =>
  texto
    .split("\n")
    .map((linea) => linea.trim())
    .filter(Boolean)
const unirLineas = (valores: string[]) => valores.join("\n")

export default function RecorridoP01() {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null)
  const [catalogo, setCatalogo] = useState<PasoCatalogo[]>([])
  const [proyectos, setProyectos] = useState<ResumenProyecto[]>([])
  const [proyecto, setProyecto] = useState<EstadoProyecto | null>(null)
  const [contenido, setContenido] = useState("")
  const [salida, setSalida] = useState<SalidaP01>(salidaInicial)
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

  const hidratarFormulario = useCallback((estado: EstadoProyecto) => {
    const pasoP01 = estado.pasos.find((paso) => paso.codigo === "P01")
    setContenido(pasoP01?.contenido_md ?? "")
    setSalida(
      pasoP01?.datos_salida && "temas_propuestos" in pasoP01.datos_salida
        ? pasoP01.datos_salida as SalidaP01
        : salidaInicial(),
    )
  }, [])

  const abrirProyecto = useCallback(
    async (idProyecto: string) => {
      if (!idProyecto) return
      setCargandoProyecto(true)
      setError("")
      setConflicto("")
      setConfirmacion("")
      try {
        const estado = await api.consultarProyecto(idProyecto)
        setProyecto(estado)
        hidratarFormulario(estado)
      } catch (errorDesconocido) {
        setError(mensajeError(errorDesconocido))
      } finally {
        setCargandoProyecto(false)
      }
    },
    [hidratarFormulario],
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
      if (lista.length > 0) await abrirProyecto(lista[0].id_proyecto)
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

  const pasoCatalogoP01 = useMemo(
    () => catalogo.find((paso) => paso.codigo === "P01"),
    [catalogo],
  )
  const estadoP01 = useMemo(
    () => proyecto?.pasos.find((paso) => paso.codigo === "P01"),
    [proyecto],
  )

  function actualizarTema(id: number, cambio: Partial<TemaCandidato>) {
    setSalida((actual) => ({
      ...actual,
      temas_propuestos: actual.temas_propuestos.map((tema) =>
        tema.id === id ? { ...tema, ...cambio } : tema,
      ),
    }))
  }

  function agregarTema() {
    if (salida.temas_propuestos.length >= 10) return
    const siguienteId =
      Math.max(...salida.temas_propuestos.map((tema) => tema.id), 0) + 1
    setSalida((actual) => ({
      ...actual,
      temas_propuestos: [
        ...actual.temas_propuestos,
        crearTemaVacio(siguienteId),
      ],
    }))
  }

  function quitarTema(id: number) {
    if (salida.temas_propuestos.length <= 5) return
    setSalida((actual) => ({
      temas_propuestos: actual.temas_propuestos.filter(
        (tema) => tema.id !== id,
      ),
      tema_preseleccionado_id:
        actual.tema_preseleccionado_id === id
          ? null
          : actual.tema_preseleccionado_id,
    }))
  }

  async function crearProyecto(evento: FormEvent) {
    evento.preventDefault()
    setCreando(true)
    setError("")
    try {
      const creado = await api.crearProyecto(nombreNuevo, tituloNuevo)
      setProyectos(await api.listarProyectos())
      setProyecto(creado)
      hidratarFormulario(creado)
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
    setGuardando(true)
    setError("")
    setConflicto("")
    setConfirmacion("")
    try {
      await api.guardarP01(
        proyecto.id_proyecto,
        contenido,
        salida,
        proyecto.version_estado,
        crypto.randomUUID(),
      )
      const actualizado = await api.consultarProyecto(proyecto.id_proyecto)
      setProyecto(actualizado)
      hidratarFormulario(actualizado)
      setConfirmacion(
        "P01 se guardó y se recargó desde PostgreSQL; el contenido persistió.",
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

  if (cargando)
    return (
      <div className="estado-pantalla">
        Cargando sesión, proyectos y metodología…
      </div>
    )
  if (sinSesion)
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

  return (
    <div className="app-shell">
      <aside className="sidebar barra-metodologia">
        <div className="brand">
          <div className="brand-mark">T</div>
          <div>
            <b>TesisMCP</b>
            <span>Ruta metodológica real</span>
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
        <nav className="arbol-pasos" aria-label="Recorrido implementado">
          <section>
            <h2>Primer recorrido vertical</h2>
            <button className="paso-activo" type="button">
              <span>P01</span>
              <span>
                <b>{pasoCatalogoP01?.nombre ?? "Mapa de temas viables"}</b>
                <small>
                  {etiquetasEstado[estadoP01?.estado ?? "DISPONIBLE"]}
                </small>
              </span>
            </button>
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
            <strong>› P01 · Mapa de temas viables</strong>
          </div>
          {proyecto && (
            <span className="version-real">
              Versión {proyecto.version_estado}
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
              <span className="eyebrow blue">PRIMER PROYECTO</span>
              <h1>Crea un proyecto para comenzar P01</h1>
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
          <form className="pagina-p01" onSubmit={guardar}>
            <section className="cabecera-p01">
              <div>
                <span className="eyebrow blue">PRIMER RECORRIDO · P01</span>
                <h1>{pasoCatalogoP01?.nombre}</h1>
                <p>{pasoCatalogoP01?.objetivo}</p>
                <p className="dependencias-p01">
                  Dependencias:{" "}
                  {pasoCatalogoP01?.dependencias.length
                    ? pasoCatalogoP01.dependencias.join(", ")
                    : "ninguna"}
                </p>
              </div>
              <div className="estado-paso-real">
                <small>Estado real</small>
                <strong>
                  {etiquetasEstado[estadoP01?.estado ?? "DISPONIBLE"]}
                </strong>
              </div>
            </section>
            {(error || conflicto || confirmacion) && (
              <div
                className={`aviso ${
                  conflicto
                    ? "aviso-conflicto"
                    : error
                      ? "aviso-error"
                      : "aviso-exito"
                }`}
                role="alert"
              >
                <span>{conflicto || error || confirmacion}</span>
                {conflicto && (
                  <button
                    type="button"
                    onClick={() => void abrirProyecto(proyecto.id_proyecto)}
                  >
                    Recargar versión actual
                  </button>
                )}
              </div>
            )}
            <div className="rejilla-p01">
              <section className="tarjeta-formulario">
                <div className="titulo-seccion">
                  <div>
                    <h2>Datos de salida</h2>
                    <p>El contrato P01 exige entre 5 y 10 temas.</p>
                  </div>
                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={agregarTema}
                    disabled={salida.temas_propuestos.length >= 10}
                  >
                    Añadir tema
                  </button>
                </div>
                <div className="lista-temas">
                  {salida.temas_propuestos.map((tema) => (
                    <fieldset key={tema.id} className="tema-candidato">
                      <legend>Tema {tema.id}</legend>
                      <button
                        type="button"
                        className="quitar-tema"
                        onClick={() => quitarTema(tema.id)}
                        disabled={salida.temas_propuestos.length <= 5}
                      >
                        Quitar
                      </button>
                      <label className="campo-ancho">
                        Título tentativo
                        <input
                          required
                          minLength={10}
                          maxLength={200}
                          value={tema.titulo_tentativo}
                          onChange={(evento) =>
                            actualizarTema(tema.id, {
                              titulo_tentativo: evento.target.value,
                            })
                          }
                        />
                      </label>
                      <label>
                        Pros (uno por línea)
                        <textarea
                          required
                          value={unirLineas(tema.pros)}
                          onChange={(evento) =>
                            actualizarTema(tema.id, {
                              pros: separarLineas(evento.target.value),
                            })
                          }
                        />
                      </label>
                      <label>
                        Contras (uno por línea)
                        <textarea
                          required
                          value={unirLineas(tema.contras)}
                          onChange={(evento) =>
                            actualizarTema(tema.id, {
                              contras: separarLineas(evento.target.value),
                            })
                          }
                        />
                      </label>
                      <label>
                        Viabilidad preliminar
                        <select
                          value={tema.viabilidad_preliminar}
                          onChange={(evento) =>
                            actualizarTema(tema.id, {
                              viabilidad_preliminar: evento.target
                                .value as TemaCandidato["viabilidad_preliminar"],
                            })
                          }
                        >
                          <option>ALTA</option>
                          <option>MEDIA</option>
                          <option>BAJA</option>
                        </select>
                      </label>
                    </fieldset>
                  ))}
                </div>
                <label className="campo-preseleccion">
                  Tema preseleccionado (opcional)
                  <select
                    value={salida.tema_preseleccionado_id ?? ""}
                    onChange={(evento) =>
                      setSalida((actual) => ({
                        ...actual,
                        tema_preseleccionado_id: evento.target.value
                          ? Number(evento.target.value)
                          : null,
                      }))
                    }
                  >
                    <option value="">Aún no seleccionar</option>
                    {salida.temas_propuestos.map((tema) => (
                      <option key={tema.id} value={tema.id}>
                        Tema {tema.id}
                      </option>
                    ))}
                  </select>
                </label>
              </section>
              <aside className="columna-narrativa">
                <section className="tarjeta-formulario">
                  <h2>Contenido narrativo</h2>
                  <p>
                    Se guarda como contenido_md junto con los datos
                    estructurados de P01.
                  </p>
                  <label>
                    Justificación y notas metodológicas
                    <textarea
                      className="editor-narrativo"
                      required
                      maxLength={200000}
                      value={contenido}
                      onChange={(evento) => setContenido(evento.target.value)}
                    />
                  </label>
                </section>
                <section className="tarjeta-formulario resumen-guardado">
                  <h2>Guardado controlado</h2>
                  <ul>
                    <li>Versión esperada: {proyecto.version_estado}</li>
                    <li>Se genera un UUID nuevo en cada intento.</li>
                    <li>
                      Un conflicto nunca sobrescribe la versión persistida.
                    </li>
                  </ul>
                  <button
                    className="button button-primary boton-guardar"
                    type="submit"
                    disabled={guardando || cargandoProyecto}
                  >
                    {guardando ? "Guardando…" : "Guardar P01"}
                  </button>
                </section>
                <section
                  className="tarjeta-formulario panel-proximamente"
                  aria-disabled="true"
                >
                  <span className="eyebrow">ASISTENTE DE TESIS</span>
                  <h2>Chat · Próximamente</h2>
                  <p>Este panel todavía no está conectado a ningún agente.</p>
                  <textarea
                    disabled
                    placeholder="Próximamente"
                    aria-label="Chat próximamente"
                  />
                  <button
                    className="button button-secondary"
                    type="button"
                    disabled
                  >
                    Próximamente
                  </button>
                </section>
              </aside>
            </div>
          </form>
        )}
      </main>
    </div>
  )
}
