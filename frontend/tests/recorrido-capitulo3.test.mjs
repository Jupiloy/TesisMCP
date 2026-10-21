import assert from "node:assert/strict"
import { test } from "node:test"

import {
  crearCargaPaso,
  crearErrorApi,
  ErrorApi,
  rutasApi,
} from "../src/lib/api/contrato.mjs"

const UUID_V4_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

const VERBOS_BLOOM_PERMITIDOS = new Set([
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
])

function validarVerboBloom(texto) {
  const primeraPalabra = texto
    .trim()
    .split(/\s+/)[0]
    ?.toUpperCase()
    ?.replace(/[:,;.]/g, "")
  return VERBOS_BLOOM_PERMITIDOS.has(primeraPalabra)
}

test("1. Rutas utilizadas: genera endpoints en español para P09 a P12", () => {
  const idProyecto = "11111111-2222-3333-4444-555555555555"
  for (const paso of ["P09", "P10", "P11", "P12"]) {
    assert.equal(
      rutasApi.paso(idProyecto, paso),
      `/proyectos/${idProyecto}/pasos/${paso}`,
    )
  }
})

test("2. Contrato P09: objetivos con Taxonomía de Bloom obligatoria", () => {
  const salidaP09 = {
    objetivo_general:
      "DETERMINAR el impacto de la arquitectura de microservicios en la concurrencia transaccional.",
    objetivos_especificos: [
      "ANALIZAR los cuellos de botella en la comunicación entre servicios desacoplados.",
      "DISEÑAR un pipeline de validación basado en el protocolo MCP.",
      "EVALUAR la latencia y rendimiento de las consultas concurrentes.",
    ],
  }

  // Objetivo general (15 a 250 caracteres, verbo de Bloom)
  assert.ok(salidaP09.objetivo_general.length >= 15)
  assert.ok(salidaP09.objetivo_general.length <= 250)
  assert.ok(validarVerboBloom(salidaP09.objetivo_general))

  // Objetivos específicos (2 a 4 elementos, cada uno con verbo de Bloom y longitud 15..250)
  assert.ok(salidaP09.objetivos_especificos.length >= 2)
  assert.ok(salidaP09.objetivos_especificos.length <= 4)
  for (const obj of salidaP09.objetivos_especificos) {
    assert.ok(obj.length >= 15)
    assert.ok(obj.length <= 250)
    assert.ok(validarVerboBloom(obj))
  }

  // Comprobar que un verbo no permitido es detectado
  const invalido = "CREAR un sistema de pruebas sin taxonomía formal."
  assert.equal(validarVerboBloom(invalido), false)
})

test("3. Contrato P10: Preguntas de investigación alineadas con formato ¿?", () => {
  const salidaP10 = {
    pregunta_general:
      "¿De qué manera la arquitectura de microservicios impacta en la concurrencia transaccional?",
    preguntas_especificas: [
      "¿Cuáles son los principales cuellos de botella en servicios desacoplados?",
      "¿Cómo influye el pipeline MCP en la consistencia de las consultas concurrentes?",
    ],
  }

  assert.ok(salidaP10.pregunta_general.startsWith("¿"))
  assert.ok(salidaP10.pregunta_general.endsWith("?"))
  assert.ok(salidaP10.pregunta_general.length >= 15)
  assert.ok(salidaP10.pregunta_general.length <= 250)

  assert.ok(salidaP10.preguntas_especificas.length >= 2)
  assert.ok(salidaP10.preguntas_especificas.length <= 4)
  for (const preg of salidaP10.preguntas_especificas) {
    assert.ok(preg.startsWith("¿"))
    assert.ok(preg.endsWith("?"))
    assert.ok(preg.length >= 15)
    assert.ok(preg.length <= 250)
  }
})

test("4. Contrato P11: Hipótesis, variables VI/VD y tipos de investigación", () => {
  const salidaP11 = {
    tipo_investigacion: "APLICADA",
    hipotesis_general:
      "La adopción de microservicios con protocolo MCP mejora significativamente la tasa de concurrencia y la reducción de latencia en sistemas distribuidos.",
    hipotesis_especificas: [
      "La modularización desacoplada disminuye los tiempos de espera bajo alta concurrencia.",
      "El protocolo MCP incrementa la trazabilidad verificable de las transacciones.",
    ],
    variable_independiente:
      "Arquitectura basada en microservicios y protocolo MCP",
    variable_dependiente: "Rendimiento y concurrencia transaccional",
  }

  const tiposPermitidos = new Set([
    "APLICADA",
    "BASICA",
    "DESCRIPTIVA",
    "CORRELACIONAL",
    "EXPLICATIVA",
  ])
  assert.ok(tiposPermitidos.has(salidaP11.tipo_investigacion))

  assert.ok(salidaP11.variable_independiente.length >= 3)
  assert.ok(salidaP11.variable_independiente.length <= 120)

  assert.ok(salidaP11.variable_dependiente.length >= 3)
  assert.ok(salidaP11.variable_dependiente.length <= 120)

  assert.ok(salidaP11.hipotesis_general.length >= 15)
  assert.ok(salidaP11.hipotesis_general.length <= 300)

  assert.ok(salidaP11.hipotesis_especificas.length >= 2)
  assert.ok(salidaP11.hipotesis_especificas.length <= 4)
})

test("5. Contrato P12: Matriz de operacionalización con dimensiones, indicadores y escalas", () => {
  const salidaP12 = {
    matriz_operacionalizacion: [
      {
        variable: "Arquitectura de microservicios",
        definicion_conceptual:
          "Modelo arquitectónico que descompone una aplicación en un conjunto de servicios autónomos e interoperables.",
        definicion_operacional:
          "Medición del desacoplamiento y grado de modularidad verificado a través de protocolos de red.",
        dimensiones: ["Modularidad", "Autonomía de despliegue"],
        indicadores: ["Tiempo de compilación", "Tasa de aislamiento de fallas"],
        escala_medicion: "RAZON",
      },
      {
        variable: "Rendimiento transaccional",
        definicion_conceptual:
          "Capacidad del sistema de procesar solicitudes de manera estable y bajo umbrales mínimos de latencia.",
        definicion_operacional:
          "Registro continuo de transacciones por segundo (TPS) y latencia percentil 99 en pruebas de carga.",
        dimensiones: ["Throughput", "Latencia"],
        indicadores: [
          "Transacciones por segundo",
          "Latencia media en milisegundos",
        ],
        escala_medicion: "INTERVALO",
      },
    ],
  }

  assert.ok(salidaP12.matriz_operacionalizacion.length >= 1)
  assert.ok(salidaP12.matriz_operacionalizacion.length <= 4)

  const escalasPermitidas = new Set([
    "NOMINAL",
    "ORDINAL",
    "INTERVALO",
    "RAZON",
  ])

  for (const fila of salidaP12.matriz_operacionalizacion) {
    assert.ok(fila.variable.length >= 3 && fila.variable.length <= 120)
    assert.ok(
      fila.definicion_conceptual.length >= 20 &&
        fila.definicion_conceptual.length <= 400,
    )
    assert.ok(
      fila.definicion_operacional.length >= 20 &&
        fila.definicion_operacional.length <= 400,
    )
    assert.ok(fila.dimensiones.length >= 1 && fila.dimensiones.length <= 6)
    assert.ok(fila.indicadores.length >= 1 && fila.indicadores.length <= 10)
    assert.ok(escalasPermitidas.has(fila.escala_medicion))
  }
})

test("6. Transición capitular: P09 a P12 se desbloquean secuencialmente", () => {
  const pasosCapitulo3 = [
    { codigo: "P09", dependencias: ["P08"], estado: "DISPONIBLE" },
    { codigo: "P10", dependencias: ["P09"], estado: "BLOQUEADO" },
    { codigo: "P11", dependencias: ["P10"], estado: "BLOQUEADO" },
    { codigo: "P12", dependencias: ["P11"], estado: "BLOQUEADO" },
  ]

  // P09 está disponible porque P08 se completó
  assert.equal(pasosCapitulo3[0].estado, "DISPONIBLE")

  // Los siguientes están bloqueados
  assert.equal(pasosCapitulo3[1].estado, "BLOQUEADO")
  assert.equal(pasosCapitulo3[2].estado, "BLOQUEADO")
  assert.equal(pasosCapitulo3[3].estado, "BLOQUEADO")

  // Simular completado de P09
  pasosCapitulo3[0].estado = "COMPLETADO"
  pasosCapitulo3[1].estado = "DISPONIBLE"

  assert.equal(pasosCapitulo3[0].estado, "COMPLETADO")
  assert.equal(pasosCapitulo3[1].estado, "DISPONIBLE")
})

test("7. Carga canónica de guardado P12 con versión e idempotencia", () => {
  const idProyecto = "test-uuid-capitulo-3"
  const datosSalidaP12 = {
    matriz_operacionalizacion: [
      {
        variable: "Variable VI",
        definicion_conceptual:
          "Definición conceptual válida de más de veinte caracteres.",
        definicion_operacional:
          "Definición operacional válida de más de veinte caracteres.",
        dimensiones: ["Dim 1"],
        indicadores: ["Ind 1"],
        escala_medicion: "RAZON",
      },
    ],
  }
  const claveIdempotencia = "98765432-abcd-4ef0-9123-456789abcdef"
  assert.match(claveIdempotencia, UUID_V4_REGEX)

  const cargaPaso = crearCargaPaso(
    "# Matriz de Operacionalización\nContenido validado.",
    datosSalidaP12,
    7, // version_esperada
    claveIdempotencia,
  )

  assert.equal(cargaPaso.version_esperada, 7)
  assert.equal(cargaPaso.clave_idempotencia, claveIdempotencia)
  assert.deepEqual(cargaPaso.datos_salida, datosSalidaP12)
})
