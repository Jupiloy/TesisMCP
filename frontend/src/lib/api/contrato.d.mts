export declare class ErrorApi extends Error {
  estadoHttp: number
  codigo: string
  detalle: string
  constructor(estadoHttp: number, codigo: string, mensaje: string, detalle: string)
}

export declare const rutasApi: Readonly<{
  sesionActual: string
  catalogoMetodologia: string
  proyectos: string
  proyecto: (idProyecto: string) => string
  paso: (idProyecto: string, codigoPaso: string) => string
  pasoP01: (idProyecto: string) => string
}>

export declare function crearCargaProyecto(nombre: string, titulo: string): {
  nombre: string
  titulo: string | null
}

export declare function crearCargaPaso<T>(
  contenidoMd: string,
  datosSalida: T,
  versionEsperada: number,
  claveIdempotencia: string,
): {
  contenido_md: string
  datos_salida: T
  version_esperada: number
  clave_idempotencia: string
}

export declare function crearCargaP01<T>(
  contenidoMd: string,
  datosSalida: T,
  versionEsperada: number,
  claveIdempotencia: string,
): {
  contenido_md: string
  datos_salida: T
  version_esperada: number
  clave_idempotencia: string
}

export declare function crearErrorApi(
  estadoHttp: number,
  errorPublico: { codigo?: string; mensaje?: string; detalle?: string },
): ErrorApi
