export class ErrorApi extends Error {
  constructor(estadoHttp, codigo, mensaje, detalle) {
    super(mensaje)
    this.name = "ErrorApi"
    this.estadoHttp = estadoHttp
    this.codigo = codigo
    this.detalle = detalle
  }
}

export const rutasApi = Object.freeze({
  sesionActual: "/sesion/actual",
  catalogoMetodologia: "/metodologia/catalogo",
  proyectos: "/proyectos",
  proyecto: (idProyecto) => `/proyectos/${idProyecto}`,
  paso: (idProyecto, codigoPaso) =>
    `/proyectos/${idProyecto}/pasos/${codigoPaso}`,
  pasoP01: (idProyecto) => `/proyectos/${idProyecto}/pasos/P01`,
})

export const crearCargaProyecto = (nombre, titulo) => ({
  nombre,
  titulo: titulo || null,
})

export const crearCargaPaso = (
  contenidoMd,
  datosSalida,
  versionEsperada,
  claveIdempotencia,
) => ({
  contenido_md: contenidoMd,
  datos_salida: datosSalida,
  version_esperada: versionEsperada,
  clave_idempotencia: claveIdempotencia,
})

export const crearCargaP01 = (
  contenidoMd,
  datosSalida,
  versionEsperada,
  claveIdempotencia,
) =>
  crearCargaPaso(
    contenidoMd,
    datosSalida,
    versionEsperada,
    claveIdempotencia,
  )

export function crearErrorApi(estadoHttp, errorPublico) {
  const codigo =
    errorPublico.codigo ??
    (estadoHttp === 401 ? "NO_AUTENTICADO" : "ERROR_HTTP")
  const mensaje = errorPublico.mensaje ?? `La solicitud falló (${estadoHttp}).`
  const detalle =
    errorPublico.detalle ?? "El servidor no proporcionó detalles adicionales."
  return new ErrorApi(estadoHttp, codigo, mensaje, detalle)
}
