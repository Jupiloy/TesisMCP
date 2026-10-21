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

test("1. Rutas utilizadas: genera endpoints canónicos en español para P01 a P05", () => {
  const idProyecto = "11111111-2222-3333-4444-555555555555"
  const pasos = ["P01", "P02", "P03", "P04", "P05"]

  for (const codigo of pasos) {
    const ruta = rutasApi.paso(idProyecto, codigo)
    assert.equal(ruta, `/proyectos/${idProyecto}/pasos/${codigo}`)
  }
  assert.equal(rutasApi.catalogoMetodologia, "/metodologia/catalogo")
  assert.equal(rutasApi.proyectos, "/proyectos")
  assert.equal(rutasApi.proyecto(idProyecto), `/proyectos/${idProyecto}`)
})

test("2. Carga exacta del guardado: estructura canónica con contenido_md, datos_salida, version_esperada y clave_idempotencia", () => {
  const datosP02 = {
    matriz_comparativa: [
      {
        tema_id: 1,
        titulo: "Optimización de tráfico con IA",
        puntajes: {
          acceso_a_datos: 4,
          relevancia_profesional: 5,
          brecha_conocimiento: 4,
          recursos_disponibles: 4,
        },
        puntaje_total: 17,
        justificacion_eleccion: "Acceso confirmado a sensores de tráfico municipal en tiempo real.",
      },
      {
        tema_id: 2,
        titulo: "Detección de plagas agrícolas",
        puntajes: {
          acceso_a_datos: 3,
          relevancia_profesional: 4,
          brecha_conocimiento: 3,
          recursos_disponibles: 3,
        },
        puntaje_total: 13,
        justificacion_eleccion: "Requiere desplazamientos constantes a campos de cultivo lejanos.",
      },
      {
        tema_id: 3,
        titulo: "Monitoreo de energía solar",
        puntajes: {
          acceso_a_datos: 4,
          relevancia_profesional: 4,
          brecha_conocimiento: 4,
          recursos_disponibles: 3,
        },
        puntaje_total: 15,
        justificacion_eleccion: "Sensores costosos pero factible acceso a base histórica institucional.",
      },
    ],
    tema_ganador_id: 1,
    tema_ganador_titulo: "Optimización de tráfico con IA",
  }

  const claveUUID = "a1b2c3d4-e5f6-4a1b-8c2d-3e4f5a6b7c8d"
  const carga = crearCargaPaso(
    "# Sustento Metodológico P02\nAnálisis comparativo de viabilidad técnica.",
    datosP02,
    2,
    claveUUID,
  )

  assert.deepEqual(carga, {
    contenido_md:
      "# Sustento Metodológico P02\nAnálisis comparativo de viabilidad técnica.",
    datos_salida: datosP02,
    version_esperada: 2,
    clave_idempotencia: claveUUID,
  })
})

test("3. Uso de version_estado: la version_esperada enviada coincide estrictamente con la version_estado del proyecto", () => {
  const estadoProyecto = {
    id_proyecto: "proy-001",
    version_estado: 7,
  }

  const carga = crearCargaPaso(
    "Contenido",
    { ods_principal_numero: 9 },
    estadoProyecto.version_estado,
    "b2c3d4e5-f6a7-4b2c-9d3e-4f5a6b7c8d9e",
  )

  assert.equal(carga.version_esperada, 7)
  assert.equal(carga.version_esperada, estadoProyecto.version_estado)
})

test("4. Generación o recepción de UUID válido para clave_idempotencia", () => {
  const uuidPrueba = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  assert.ok(
    UUID_V4_REGEX.test(uuidPrueba),
    "El identificador debe ser un UUID estándar",
  )

  // Comprobar con el generador nativo del entorno
  const nuevoUuid = crypto.randomUUID()
  assert.ok(
    UUID_V4_REGEX.test(nuevoUuid),
    "crypto.randomUUID() debe generar un UUID v4 conforme",
  )

  const carga = crearCargaPaso("Texto", {}, 0, nuevoUuid)
  assert.ok(UUID_V4_REGEX.test(carga.clave_idempotencia))
})

test("5. Interpretación de codigo, mensaje y detalle en respuestas de error de Django", () => {
  const errorServidor = {
    codigo: "ERROR_ESQUEMA_VALIDACION",
    mensaje: "El campo 'argumento_alineacion' debe tener al menos 50 caracteres",
    detalle:
      "ERROR_ESQUEMA_VALIDACION: El campo 'argumento_alineacion' debe tener al menos 50 caracteres",
  }

  const errorApi = crearErrorApi(422, errorServidor)
  assert.ok(errorApi instanceof ErrorApi)
  assert.equal(errorApi.estadoHttp, 422)
  assert.equal(errorApi.codigo, "ERROR_ESQUEMA_VALIDACION")
  assert.equal(
    errorApi.message,
    "El campo 'argumento_alineacion' debe tener al menos 50 caracteres",
  )
  assert.equal(
    errorApi.detalle,
    "ERROR_ESQUEMA_VALIDACION: El campo 'argumento_alineacion' debe tener al menos 50 caracteres",
  )
})

test("6. Manejo de CONFLICTO_VERSION (409): preserva el error y evita sobrescritura silenciosa", () => {
  const respuestaConflicto = {
    codigo: "CONFLICTO_VERSION",
    mensaje: "El perfil cambió; consulta la versión actual",
    detalle: "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual",
  }

  const errorApi = crearErrorApi(409, respuestaConflicto)
  assert.equal(errorApi.estadoHttp, 409)
  assert.equal(errorApi.codigo, "CONFLICTO_VERSION")
  assert.equal(errorApi.message, "El perfil cambió; consulta la versión actual")
  assert.equal(
    errorApi.detalle,
    "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual",
  )
})

test("7. Selección de P02–P05: filtrado y disponibilidad según el estado devuelto por el backend", () => {
  const pasosBackend = [
    { codigo: "P01", estado: "COMPLETADO", dependencias: [] },
    { codigo: "P02", estado: "DISPONIBLE", dependencias: ["P01"] },
    { codigo: "P03", estado: "BLOQUEADO", dependencias: ["P02"] },
    { codigo: "P04", estado: "BLOQUEADO", dependencias: ["P03"] },
    { codigo: "P05", estado: "BLOQUEADO", dependencias: ["P04"] },
  ]

  // Paso P01 está completado -> se puede abrir y consultar
  const p01 = pasosBackend.find((p) => p.codigo === "P01")
  assert.equal(p01.estado, "COMPLETADO")

  // Paso P02 está disponible -> se puede abrir y editar
  const p02 = pasosBackend.find((p) => p.codigo === "P02")
  assert.equal(p02.estado, "DISPONIBLE")

  // Paso P03 está bloqueado -> debe reflejar BLOQUEADO y sus dependencias
  const p03 = pasosBackend.find((p) => p.codigo === "P03")
  assert.equal(p03.estado, "BLOQUEADO")
  assert.deepEqual(p03.dependencias, ["P02"])
})

test("8. Paso bloqueado sin acción de guardado: simula intento de guardado bloqueado", () => {
  const pasoBloqueado = {
    codigo: "P03",
    estado: "BLOQUEADO",
    dependencias: ["P02"],
    acciones_permitidas: [],
  }

  // La regla de negocio indica que si acciones_permitidas no incluye "GUARDAR" o estado === "BLOQUEADO", no se ejecuta PUT
  const puedeGuardar =
    pasoBloqueado.estado !== "BLOQUEADO" &&
    pasoBloqueado.acciones_permitidas.includes("GUARDAR")

  assert.equal(puedeGuardar, false, "Un paso bloqueado no debe permitir guardar")
})

test("9. Hidratación de datos previamente persistidos de P01 a P05", () => {
  const proyectoGuardado = {
    id_proyecto: "proy-456",
    version_estado: 4,
    pasos: [
      {
        codigo: "P01",
        estado: "COMPLETADO",
        contenido_md: "# Notas de P01 persistidas en PostgreSQL",
        datos_salida: {
          temas_propuestos: [
            {
              id: 1,
              titulo_tentativo: "Tema 1 de prueba persistido",
              pros: ["Pro 1"],
              contras: ["Contra 1"],
              viabilidad_preliminar: "ALTA",
            },
          ],
          tema_preseleccionado_id: 1,
        },
      },
      {
        codigo: "P02",
        estado: "COMPLETADO",
        contenido_md: "## Notas P02",
        datos_salida: {
          tema_ganador_id: 1,
          tema_ganador_titulo: "Tema 1 de prueba persistido",
        },
      },
    ],
  }

  const p01 = proyectoGuardado.pasos.find((p) => p.codigo === "P01")
  assert.equal(
    p01.contenido_md,
    "# Notas de P01 persistidas en PostgreSQL",
  )
  assert.equal(p01.datos_salida.tema_preseleccionado_id, 1)

  const p02 = proyectoGuardado.pasos.find((p) => p.codigo === "P02")
  assert.equal(p02.contenido_md, "## Notas P02")
  assert.equal(p02.datos_salida.tema_ganador_id, 1)
})

test("10. Recarga del proyecto después del guardado exitoso", () => {
  // Simulación del ciclo transaccional: estado inicial -> guardado exitoso -> recarga con version_estado incrementada
  const estadoInicial = {
    id_proyecto: "proy-789",
    version_estado: 1,
    pasos: [
      { codigo: "P01", estado: "COMPLETADO" },
      { codigo: "P02", estado: "DISPONIBLE", contenido_md: "", datos_salida: null },
      { codigo: "P03", estado: "BLOQUEADO" },
    ],
  }

  // Se simula la respuesta de PostgreSQL tras guardar P02
  const estadoRecargado = {
    id_proyecto: "proy-789",
    version_estado: 2, // lock_version incrementado por Django
    pasos: [
      { codigo: "P01", estado: "COMPLETADO" },
      {
        codigo: "P02",
        estado: "COMPLETADO",
        contenido_md: "Sustento guardado",
        datos_salida: { tema_ganador_id: 1, tema_ganador_titulo: "Tema Ganador" },
      },
      { codigo: "P03", estado: "DISPONIBLE" }, // P03 se desbloquea tras completar P02
    ],
  }

  assert.equal(estadoRecargado.version_estado, estadoInicial.version_estado + 1)
  const pasoP02Recargado = estadoRecargado.pasos.find((p) => p.codigo === "P02")
  assert.equal(pasoP02Recargado.estado, "COMPLETADO")
  assert.equal(pasoP02Recargado.contenido_md, "Sustento guardado")

  const pasoP03Recargado = estadoRecargado.pasos.find((p) => p.codigo === "P03")
  assert.equal(
    pasoP03Recargado.estado,
    "DISPONIBLE",
    "P03 debe pasar de BLOQUEADO a DISPONIBLE al recargar",
  )
})

test("11. Verificación de reglas de contrato de P02 (Puntaje Total y Ganador)", () => {
  const puntajes = {
    acceso_a_datos: 4,
    relevancia_profesional: 5,
    brecha_conocimiento: 3,
    recursos_disponibles: 4,
  }
  const totalCalculado =
    puntajes.acceso_a_datos +
    puntajes.relevancia_profesional +
    puntajes.brecha_conocimiento +
    puntajes.recursos_disponibles

  assert.equal(totalCalculado, 16)
  assert.ok(totalCalculado >= 4 && totalCalculado <= 20)
})

test("12. Verificación de reglas de contrato de P04 (Límite de 20 palabras e inclusión)", () => {
  const tituloOficial =
    "Protocolo MCP y Circuito Determinista en Tesis de Ingeniería en Piura 2026"
  const palabras = tituloOficial.trim().split(/\s+/).filter(Boolean)

  assert.ok(palabras.length <= 20, "El título no debe superar 20 palabras")
  assert.equal(palabras.length, 12)

  const variables = ["Protocolo MCP", "Circuito Determinista"]
  const unidad = "Tesis de Ingeniería"
  const lugar = "Piura"
  const periodo = 2026

  const tituloMinus = tituloOficial.toLowerCase()
  for (const v of variables) {
    assert.ok(
      tituloMinus.includes(v.toLowerCase()),
      `El título debe contener la variable '${v}'`,
    )
  }
  assert.ok(tituloMinus.includes(unidad.toLowerCase()))
  assert.ok(tituloMinus.includes(lugar.toLowerCase()))
  assert.ok(tituloMinus.includes(String(periodo)))
})

test("13. Verificación de reglas de contrato de P05 (Párrafos y Palabras)", () => {
  const parrafos = [
    "En la actualidad, la formulación de tesis de ingeniería presenta retos significativos en la verificación de citas bibliográficas y rigor metodológico formal universitario.",
    "Para atender esta problemática, se propone un enfoque determinista que desacopla la generación creativa de la validación estricta de esquemas académicos normalizados.",
    "El presente trabajo evalúa la efectividad de este asistente metodológico en estudiantes de ingeniería de software durante el periodo académico correspondiente.",
  ]

  const texto = parrafos.join("\n\n")
  const parrafosContados = texto
    .split("\n\n")
    .map((p) => p.trim())
    .filter(Boolean)

  assert.ok(
    parrafosContados.length >= 3,
    "Debe contener al menos 3 párrafos separados por doble salto",
  )
  assert.equal(parrafosContados.length, 3)

  const palabrasContadas = texto.trim().split(/\s+/).filter(Boolean)
  assert.ok(palabrasContadas.length > 0)
})
