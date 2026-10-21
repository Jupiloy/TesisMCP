import assert from "node:assert/strict"
import { test } from "node:test"

import {
  crearCargaP01,
  crearCargaPaso,
  crearCargaProyecto,
  crearErrorApi,
  ErrorApi,
  rutasApi,
} from "../src/lib/api/contrato.mjs"

test("define las rutas reales del recorrido P01-P05 en español", () => {
  assert.equal(rutasApi.sesionActual, "/sesion/actual")
  assert.equal(rutasApi.catalogoMetodologia, "/metodologia/catalogo")
  assert.equal(rutasApi.proyectos, "/proyectos")
  assert.equal(rutasApi.proyecto("proyecto-1"), "/proyectos/proyecto-1")
  assert.equal(
    rutasApi.pasoP01("proyecto-1"),
    "/proyectos/proyecto-1/pasos/P01",
  )
  for (const paso of ["P01", "P02", "P03", "P04", "P05"]) {
    assert.equal(
      rutasApi.paso("proyecto-1", paso),
      `/proyectos/proyecto-1/pasos/${paso}`,
    )
  }
})

test("crea las cargas públicas exactas de proyecto, P01 y pasos P02 a P05", () => {
  assert.deepEqual(crearCargaProyecto("Proyecto real", "Título real"), {
    nombre: "Proyecto real",
    titulo: "Título real",
  })
  const cargaPaso = crearCargaPaso(
    "Contenido de prueba",
    { tema_ganador_id: 1 },
    3,
    "123e4567-e89b-12d3-a456-426614174000",
  )
  assert.deepEqual(cargaPaso, {
    contenido_md: "Contenido de prueba",
    datos_salida: { tema_ganador_id: 1 },
    version_esperada: 3,
    clave_idempotencia: "123e4567-e89b-12d3-a456-426614174000",
  })
  assert.deepEqual(
    crearCargaP01(
      "Contenido persistente",
      { temas_propuestos: [], tema_preseleccionado_id: null },
      0,
      "00000000-0000-4000-8000-000000000001",
    ),
    {
      contenido_md: "Contenido persistente",
      datos_salida: { temas_propuestos: [], tema_preseleccionado_id: null },
      version_esperada: 0,
      clave_idempotencia: "00000000-0000-4000-8000-000000000001",
    },
  )
})

test("conserva codigo, mensaje y detalle de CONFLICTO_VERSION", () => {
  const error = crearErrorApi(409, {
    codigo: "CONFLICTO_VERSION",
    mensaje: "El perfil cambió; consulta la versión actual",
    detalle: "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual",
  })
  assert.ok(error instanceof ErrorApi)
  assert.equal(error.estadoHttp, 409)
  assert.equal(error.codigo, "CONFLICTO_VERSION")
  assert.equal(error.message, "El perfil cambió; consulta la versión actual")
  assert.equal(
    error.detalle,
    "CONFLICTO_VERSION: El perfil cambió; consulta la versión actual",
  )
})
