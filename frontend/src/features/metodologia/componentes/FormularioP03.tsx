import type { SalidaP03 } from "../../../lib/api/cliente"

const LISTA_ODS = [
  { numero: 1, nombre: "Fin de la pobreza" },
  { numero: 2, nombre: "Hambre cero" },
  { numero: 3, nombre: "Salud y bienestar" },
  { numero: 4, nombre: "Educación de calidad" },
  { numero: 5, nombre: "Igualdad de género" },
  { numero: 6, nombre: "Agua limpia y saneamiento" },
  { numero: 7, nombre: "Energía asequible y no contaminante" },
  { numero: 8, nombre: "Trabajo decente y crecimiento económico" },
  { numero: 9, nombre: "Industria, innovación e infraestructura" },
  { numero: 10, nombre: "Reducción de las desigualdades" },
  { numero: 11, nombre: "Ciudades y comunidades sostenibles" },
  { numero: 12, nombre: "Producción y consumo responsables" },
  { numero: 13, nombre: "Acción por el clima" },
  { numero: 14, nombre: "Vida submarina" },
  { numero: 15, nombre: "Vida de ecosistemas terrestres" },
  { numero: 16, nombre: "Paz, justicia e instituciones sólidas" },
  { numero: 17, nombre: "Alianzas para lograr los objetivos" },
]

export const salidaP03Inicial = (): SalidaP03 => ({
  ods_principal_numero: 0,
  ods_principal_nombre: "",
  meta_ods_especifica: "",
  argumento_alineacion: "",
  linea_utp_vinculada: "",
})

export function normalizarSalidaP03(
  datos?: Partial<SalidaP03> | null,
): SalidaP03 {
  const base = salidaP03Inicial()
  if (!datos) return base
  return {
    ods_principal_numero:
      typeof datos.ods_principal_numero === "number"
        ? datos.ods_principal_numero
        : base.ods_principal_numero,
    ods_principal_nombre:
      datos.ods_principal_nombre ?? base.ods_principal_nombre,
    meta_ods_especifica: datos.meta_ods_especifica ?? base.meta_ods_especifica,
    argumento_alineacion:
      datos.argumento_alineacion ?? base.argumento_alineacion,
    linea_utp_vinculada: datos.linea_utp_vinculada ?? base.linea_utp_vinculada,
  }
}

interface FormularioP03Props {
  datos: SalidaP03
  alCambiarDatos: (nuevosDatos: SalidaP03) => void
  deshabilitado?: boolean
}

export default function FormularioP03({
  datos,
  alCambiarDatos,
  deshabilitado = false,
}: FormularioP03Props) {
  const datosSeguros = normalizarSalidaP03(datos)

  function seleccionarOds(numero: number) {
    const ods = LISTA_ODS.find((item) => item.numero === numero)
    if (!ods) return
    alCambiarDatos({
      ...datosSeguros,
      ods_principal_numero: ods.numero,
      ods_principal_nombre: ods.nombre,
    })
  }

  return (
    <section className="tarjeta-formulario">
      <div className="titulo-seccion">
        <div>
          <h2>Datos de salida · P03: Alineación ODS y relevancia</h2>
          <p>
            Alinea la investigación con los Objetivos de Desarrollo Sostenible
            (ODS 1 a 17) y las líneas de investigación institucionales.
          </p>
        </div>
      </div>

      <div className="lista-temas">
        <div className="fila-dos-columnas">
          <label>
            ODS Principal (1 a 17)
            <select
              value={datosSeguros.ods_principal_numero}
              onChange={(e) => seleccionarOds(Number(e.target.value))}
              disabled={deshabilitado}
            >
              <option value={0} disabled>
                Selecciona un ODS
              </option>
              {LISTA_ODS.map((ods) => (
                <option key={ods.numero} value={ods.numero}>
                  ODS {ods.numero}: {ods.nombre}
                </option>
              ))}
            </select>
          </label>

          <label>
            Nombre oficial del ODS (5 a 100 caracteres)
            <input
              required
              minLength={5}
              maxLength={100}
              value={datosSeguros.ods_principal_nombre}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  ods_principal_nombre: e.target.value,
                })
              }
              disabled={deshabilitado}
            />
          </label>
        </div>

        <div className="fila-dos-columnas">
          <label>
            Meta ODS específica (3 a 20 caracteres)
            <input
              required
              minLength={3}
              maxLength={20}
              value={datosSeguros.meta_ods_especifica}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  meta_ods_especifica: e.target.value,
                })
              }
              disabled={deshabilitado}
              placeholder="Ejemplo: ODS-09:9.5 o 9.5"
            />
          </label>

          <label>
            Línea de investigación institucional (5 a 150 caracteres)
            <input
              required
              minLength={5}
              maxLength={150}
              value={datosSeguros.linea_utp_vinculada}
              onChange={(e) =>
                alCambiarDatos({
                  ...datosSeguros,
                  linea_utp_vinculada: e.target.value,
                })
              }
              disabled={deshabilitado}
              placeholder="Ejemplo: Tecnologías de la Información y Comunicación"
            />
          </label>
        </div>

        <label className="campo-ancho">
          Argumento de alineación (50 a 600 caracteres)
          <textarea
            required
            minLength={50}
            maxLength={600}
            value={datosSeguros.argumento_alineacion}
            onChange={(e) =>
              alCambiarDatos({
                ...datosSeguros,
                argumento_alineacion: e.target.value,
              })
            }
            disabled={deshabilitado}
            placeholder="Sustenta cómo el proyecto contribuye al logro de la meta ODS seleccionada…"
            rows={4}
          />
          <span className="caracteres-ayuda">
            {datosSeguros.argumento_alineacion.length}/600 caracteres (mínimo
            50)
          </span>
        </label>
      </div>
    </section>
  )
}
