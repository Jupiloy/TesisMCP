import {
  crearCargaP01,
  crearCargaPaso,
  crearCargaProyecto,
  crearErrorApi,
  ErrorApi,
  rutasApi,
} from "./contrato.mjs"

export { ErrorApi }

export type UsuarioSesion = {
  correo: string
  nombre_visible: string
}

export type ResumenProyecto = {
  id_proyecto: string
  nombre: string
  titulo: string
  estado: "ACTIVO"
  version_estado: number
  actualizado_en: string
}

export type TemaCandidato = {
  id: number
  titulo_tentativo: string
  pros: string[]
  contras: string[]
  viabilidad_preliminar: "ALTA" | "MEDIA" | "BAJA"
}

export type SalidaP01 = {
  temas_propuestos: TemaCandidato[]
  tema_preseleccionado_id: number | null
}

export type CriterioEvaluacion = {
  acceso_a_datos: number
  relevancia_profesional: number
  brecha_conocimiento: number
  recursos_disponibles: number
}

export type EvaluacionTema = {
  tema_id: number
  titulo: string
  puntajes: CriterioEvaluacion
  puntaje_total: number
  justificacion_eleccion: string
}

export type SalidaP02 = {
  matriz_comparativa: EvaluacionTema[]
  tema_ganador_id: number
  tema_ganador_titulo: string
}

export type SalidaP03 = {
  ods_principal_numero: number
  ods_principal_nombre: string
  meta_ods_especifica: string
  argumento_alineacion: string
  linea_utp_vinculada: string
}

export type SalidaP04 = {
  titulo_oficial: string
  conteo_palabras: number
  variables_confirmadas: string[]
  unidad_analisis_confirmada: string
  lugar_confirmado: string
  periodo_confirmado: number
}

export type SalidaP05 = {
  contenido_markdown: string
  num_parrafos: number
  palabras_totales: number
}

export type SalidaP06 = {
  problema_central: string
  causas_directas: string[]
  efectos_directos: string[]
  pregunta_general: string
  preguntas_especificas: string[]
}

export type DimensionJustificacion = {
  dimension: "TEORICA" | "PRACTICA" | "METODOLOGICA" | "SOCIAL"
  argumento: string
}

export type SalidaP07 = {
  justificaciones: DimensionJustificacion[]
  resumen_ejecutivo: string
}

export type SalidaP08 = {
  brecha_detectada: string
  aporte_propuesto: string
  estado_evidencia: "EVIDENCIA_PENDIENTE"
}

export const VERBOS_BLOOM_PERMITIDOS = [
  "DETERMINAR",
  "ANALIZAR",
  "EVALUAR",
  "DISEÑAR",
  "IMPLEMENTAR",
  "PROPONER",
  "IDENTIFICAR",
  "COMPARAR",
  "ESTABLECER",
  "EXAMINAR",
  "MEDIR",
  "DEMOSTRAR",
  "OPTIMIZAR",
  "DESARROLLAR",
  "MODELAR",
] as const

export type VerboBloom = typeof VERBOS_BLOOM_PERMITIDOS[number]

export type SalidaP09 = {
  objetivo_general: string
  objetivos_especificos: string[]
}

export type SalidaP10 = {
  pregunta_general: string
  preguntas_especificas: string[]
}

export type TipoInvestigacion = "APLICADA" | "BASICA" | "DESCRIPTIVA" | "CORRELACIONAL" | "EXPLICATIVA"

export type SalidaP11 = {
  tipo_investigacion: TipoInvestigacion | ""
  hipotesis_general: string
  hipotesis_especificas: string[]
  variable_independiente: string
  variable_dependiente: string
}

export type EscalaMedicion = "NOMINAL" | "ORDINAL" | "INTERVALO" | "RAZON"

export type FilaOperacionalizacion = {
  variable: string
  definicion_conceptual: string
  definicion_operacional: string
  dimensiones: string[]
  indicadores: string[]
  escala_medicion: EscalaMedicion | ""
}

export type SalidaP12 = {
  matriz_operacionalizacion: FilaOperacionalizacion[]
}

export type DatosSalidaPaso = SalidaP01 | SalidaP02 | SalidaP03 | SalidaP04 | SalidaP05 | SalidaP06 | SalidaP07 | SalidaP08 | SalidaP09 | SalidaP10 | SalidaP11 | SalidaP12 | Record<string, unknown>

export type PasoCatalogo = {
  codigo: string
  capitulo: number
  nombre: string
  objetivo: string
  entradas_requeridas: string[]
  dependencias: string[]
  esquema_salida: Record<string, unknown>
}

export type EstadoPaso = {
  codigo: string
  estado: "COMPLETADO" | "DISPONIBLE" | "BLOQUEADO"
  dependencias: string[]
  acciones_permitidas: string[]
  datos_salida: DatosSalidaPaso | null
  contenido_md: string
}

export type EstadoProyecto = {
  id_proyecto: string
  nombre: string
  titulo: string
  estado: "ACTIVO"
  version_estado: number
  pasos: EstadoPaso[]
}

type DetalleError = {
  codigo?: string
  mensaje?: string
  detalle?: string
}

function leerCookie(nombre: string): string {
  if (typeof document === "undefined") return ""
  const prefijo = `${nombre}=`
  const parte = document.cookie
    .split(";")
    .map((valor) => valor.trim())
    .find((valor) => valor.startsWith(prefijo))
  return parte ? decodeURIComponent(parte.slice(prefijo.length)) : ""
}

async function solicitar<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  const metodo = opciones.method?.toUpperCase() ?? "GET"
  const headers = new Headers(opciones.headers)
  headers.set("Accept", "application/json")
  if (opciones.body) headers.set("Content-Type", "application/json")
  if (!["GET", "HEAD", "OPTIONS"].includes(metodo))
    headers.set("X-CSRFToken", leerCookie("csrftoken"))
  const respuesta = await fetch(`/api/v1${ruta}`, {
    ...opciones,
    headers,
    credentials: "same-origin",
  })
  if (!respuesta.ok) {
    let errorPublico: DetalleError = {}
    try {
      errorPublico = ((await respuesta.json()) as DetalleError)
    } catch {
      errorPublico = {}
    }
    throw crearErrorApi(respuesta.status, errorPublico)
  }
  return (await respuesta.json()) as T
}

export const api = {
  consultarSesion: () => solicitar<UsuarioSesion>(rutasApi.sesionActual),
  consultarCatalogo: () =>
    solicitar<PasoCatalogo[]>(rutasApi.catalogoMetodologia),
  listarProyectos: () => solicitar<ResumenProyecto[]>(rutasApi.proyectos),
  consultarProyecto: (idProyecto: string) =>
    solicitar<EstadoProyecto>(rutasApi.proyecto(idProyecto)),
  crearProyecto: (nombre: string, titulo: string) =>
    solicitar<EstadoProyecto>(rutasApi.proyectos, {
      method: "POST",
      body: JSON.stringify(crearCargaProyecto(nombre, titulo)),
    }),
  guardarPaso: (
    idProyecto: string,
    codigoPaso: string,
    contenidoMd: string,
    datosSalida: Record<string, unknown>,
    versionEsperada: number,
    claveIdempotencia: string,
  ) =>
    solicitar<{ version_estado: number }>(
      rutasApi.paso(idProyecto, codigoPaso),
      {
        method: "PUT",
        body: JSON.stringify(
          crearCargaPaso(
            contenidoMd,
            datosSalida,
            versionEsperada,
            claveIdempotencia,
          ),
        ),
      },
    ),
  guardarP01: (
    idProyecto: string,
    contenidoMd: string,
    datosSalida: SalidaP01,
    versionEsperada: number,
    claveIdempotencia: string,
  ) =>
    solicitar<{ version_estado: number }>(rutasApi.pasoP01(idProyecto), {
      method: "PUT",
      body: JSON.stringify(
        crearCargaP01(
          contenidoMd,
          datosSalida,
          versionEsperada,
          claveIdempotencia,
        ),
      ),
    }),
}
