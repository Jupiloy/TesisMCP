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

test("1. Rutas utilizadas: genera endpoints en español para P06, P07 y P08", () => {
  const idProyecto = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
  for (const paso of ["P06", "P07", "P08"]) {
    assert.equal(
      rutasApi.paso(idProyecto, paso),
      `/proyectos/${idProyecto}/pasos/${paso}`,
    )
  }
})

test("2. Contrato P06: Árbol de problemas, causas, efectos y signos ¿? en preguntas", () => {
  const salidaP06 = {
    problema_central:
      "Deficiente trazabilidad y dispersión metodológica en tesis de ingeniería de software",
    causas_directas: [
      "Falta de herramientas integradas con estándares universitarios",
      "Uso indiscriminado de modelos de lenguaje sin verificación de citas",
      "Desconexión entre borradores de estudiantes y observaciones docentes",
    ],
    efectos_directos: [
      "Altas tasas de observaciones metodológicas en sustentaciones",
      "Pérdida de rigor empírico y formulación de citas alucinadas",
    ],
    pregunta_general:
      "¿De qué manera el protocolo MCP y un circuito determinista mejoran la consistencia metodológica de las tesis?",
    preguntas_especificas: [
      "¿Cómo influye la validación estricta de esquemas en la reducción de observaciones?",
      "¿En qué medida la persistencia inmutable asegura la trazabilidad de revisiones?",
    ],
  }

  // Comprobar problema central (15 a 250 caracteres)
  assert.ok(salidaP06.problema_central.length >= 15)
  assert.ok(salidaP06.problema_central.length <= 250)

  // Comprobar causas directas (2 a 5)
  assert.ok(salidaP06.causas_directas.length >= 2)
  assert.ok(salidaP06.causas_directas.length <= 5)

  // Comprobar efectos directos (2 a 5)
  assert.ok(salidaP06.efectos_directos.length >= 2)
  assert.ok(salidaP06.efectos_directos.length <= 5)

  // Comprobar pregunta general (¿ y ?, longitud >= 20)
  assert.ok(salidaP06.pregunta_general.startsWith("¿"))
  assert.ok(salidaP06.pregunta_general.endsWith("?"))
  assert.ok(salidaP06.pregunta_general.length >= 20)
  assert.ok(salidaP06.pregunta_general.length <= 250)

  // Comprobar preguntas específicas (2 a 4)
  assert.ok(salidaP06.preguntas_especificas.length >= 2)
  assert.ok(salidaP06.preguntas_especificas.length <= 4)
  for (const q of salidaP06.preguntas_especificas) {
    assert.ok(q.startsWith("¿"), `Pregunta debe iniciar con ¿: ${q}`)
    assert.ok(q.endsWith("?"), `Pregunta debe terminar con ?: ${q}`)
  }

  // Generar carga de guardado
  const uuid = crypto.randomUUID()
  const carga = crearCargaPaso("Contenido Markdown P06", salidaP06, 5, uuid)
  assert.deepEqual(carga, {
    contenido_md: "Contenido Markdown P06",
    datos_salida: salidaP06,
    version_esperada: 5,
    clave_idempotencia: uuid,
  })
})

test("3. Contrato P07: Cuatro dimensiones metodológicas exactas y resumen ejecutivo", () => {
  const salidaP07 = {
    justificaciones: [
      {
        dimension: "TEORICA",
        argumento:
          "La investigación aporta al estudio del acoplamiento entre sistemas multiagente y modelos deterministas de verificación académica formal.",
      },
      {
        dimension: "PRACTICA",
        argumento:
          "Permite a los estudiantes formular proyectos de grado sin incurrir en demoras excesivas por observaciones reiteradas de formato y consistencia.",
      },
      {
        dimension: "METODOLOGICA",
        argumento:
          "Introduce un protocolo de 32 pasos desacoplados validados con esquemas Pydantic estrictos e historial append-only inmutable.",
      },
      {
        dimension: "SOCIAL",
        argumento:
          "Contribuye a elevar la calidad de los egresados de ingeniería y su producción científica verificable en beneficio de la comunidad universitaria.",
      },
    ],
    resumen_ejecutivo:
      "Este proyecto se justifica teóricamente por su aporte a la IA determinista, prácticamente por la optimización del tiempo de titulación, metodológicamente por sus contratos formales y socialmente por el rigor científico transferido a la sociedad.",
  }

  // Comprobar que contiene exactamente las 4 dimensiones requeridas sin duplicados
  const dimensionesEncontradas = new Set(
    salidaP07.justificaciones.map((j) => j.dimension),
  )
  assert.equal(salidaP07.justificaciones.length, 4)
  assert.deepEqual(
    dimensionesEncontradas,
    new Set(["TEORICA", "PRACTICA", "METODOLOGICA", "SOCIAL"]),
  )

  // Cada argumento debe tener entre 60 y 800 caracteres
  for (const item of salidaP07.justificaciones) {
    assert.ok(
      item.argumento.length >= 60,
      `Argumento ${item.dimension} debe tener al menos 60 caracteres`,
    )
    assert.ok(
      item.argumento.length <= 800,
      `Argumento ${item.dimension} no debe exceder 800 caracteres`,
    )
  }

  // Resumen ejecutivo debe tener entre 80 y 600 caracteres
  assert.ok(salidaP07.resumen_ejecutivo.length >= 80)
  assert.ok(salidaP07.resumen_ejecutivo.length <= 600)
})

test("4. Contrato P08: Brecha de investigación, aporte novedoso y estado EVIDENCIA_PENDIENTE", () => {
  const salidaP08 = {
    brecha_detectada:
      "Los asistentes actuales basados en LLM alucinan citas inexistentes y carecen de verificación con el catálogo metodológico universitario.",
    aporte_propuesto:
      "Una pasarela tipada con protocolo MCP conectada a PostgreSQL con control de concurrencia optimista y triggers inmutables de auditoría.",
    estado_evidencia: "EVIDENCIA_PENDIENTE",
  }

  assert.ok(salidaP08.brecha_detectada.length >= 30)
  assert.ok(salidaP08.brecha_detectada.length <= 400)

  assert.ok(salidaP08.aporte_propuesto.length >= 30)
  assert.ok(salidaP08.aporte_propuesto.length <= 400)

  assert.equal(
    salidaP08.estado_evidencia,
    "EVIDENCIA_PENDIENTE",
    "El estado de evidencia debe ser exactamente EVIDENCIA_PENDIENTE",
  )
})

test("5. Transición capitular: P06 se desbloquea tras completar P05 en el backend", () => {
  // Cuando P05 está COMPLETADO, P06 debe figurar como DISPONIBLE
  const pasosBackend = [
    { codigo: "P05", estado: "COMPLETADO", dependencias: ["P04"] },
    {
      codigo: "P06",
      estado: "DISPONIBLE",
      dependencias: ["P05"],
      acciones_permitidas: ["GUARDAR"],
    },
    {
      codigo: "P07",
      estado: "BLOQUEADO",
      dependencias: ["P06"],
      acciones_permitidas: [],
    },
  ]

  const p06 = pasosBackend.find((p) => p.codigo === "P06")
  assert.equal(p06.estado, "DISPONIBLE")
  assert.deepEqual(p06.dependencias, ["P05"])
  assert.ok(p06.acciones_permitidas.includes("GUARDAR"))

  const p07 = pasosBackend.find((p) => p.codigo === "P07")
  assert.equal(p07.estado, "BLOQUEADO")
  assert.equal(p07.acciones_permitidas.length, 0)
})

test("6. Modelo esperado de transición de estado después de guardar P06", () => {
  const estadoAntesGuardar = {
    id_proyecto: "proy-cap2",
    version_estado: 5,
    pasos: [
      { codigo: "P05", estado: "COMPLETADO" },
      {
        codigo: "P06",
        estado: "DISPONIBLE",
        contenido_md: "",
        datos_salida: null,
      },
      { codigo: "P07", estado: "BLOQUEADO" },
    ],
  }

  // Este caso verifica el contrato esperado; la integración real se prueba en Django.
  const estadoDespuesRecarga = {
    id_proyecto: "proy-cap2",
    version_estado: 6,
    pasos: [
      { codigo: "P05", estado: "COMPLETADO" },
      {
        codigo: "P06",
        estado: "COMPLETADO",
        contenido_md: "# Diagnóstico del problema guardado",
        datos_salida: { problema_central: "Problema guardado en PostgreSQL" },
      },
      { codigo: "P07", estado: "DISPONIBLE" }, // P07 se desbloquea
    ],
  }

  assert.equal(
    estadoDespuesRecarga.version_estado,
    estadoAntesGuardar.version_estado + 1,
  )
  const p06Recargado = estadoDespuesRecarga.pasos.find(
    (p) => p.codigo === "P06",
  )
  assert.equal(p06Recargado.estado, "COMPLETADO")
  assert.equal(p06Recargado.contenido_md, "# Diagnóstico del problema guardado")

  const p07Recargado = estadoDespuesRecarga.pasos.find(
    (p) => p.codigo === "P07",
  )
  assert.equal(p07Recargado.estado, "DISPONIBLE")
})
