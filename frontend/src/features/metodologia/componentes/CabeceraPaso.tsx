import type { EstadoPaso, PasoCatalogo } from "../../../lib/api/cliente"

const etiquetasEstado = {
  COMPLETADO: "Completado",
  DISPONIBLE: "Disponible",
  BLOQUEADO: "Bloqueado",
} as const

interface CabeceraPasoProps {
  pasoCatalogo?: PasoCatalogo
  estadoPaso?: EstadoPaso
  codigoPaso: string
}

export default function CabeceraPaso({
  pasoCatalogo,
  estadoPaso,
  codigoPaso,
}: CabeceraPasoProps) {
  const estado = estadoPaso?.estado ?? "DISPONIBLE"
  const dependencias = estadoPaso?.dependencias ?? pasoCatalogo?.dependencias ?? []

  return (
    <section className="cabecera-p01">
      <div>
        <span className="eyebrow blue">
          CAPÍTULO {pasoCatalogo?.capitulo ?? (["P06", "P07", "P08"].includes(codigoPaso) ? 2 : ["P09", "P10", "P11", "P12"].includes(codigoPaso) ? 3 : 1)} · {codigoPaso}
        </span>
        <h1>{pasoCatalogo?.nombre ?? codigoPaso}</h1>
        <p>{pasoCatalogo?.objetivo}</p>
        <p className="dependencias-p01">
          Dependencias:{" "}
          {dependencias.length > 0 ? dependencias.join(", ") : "ninguna"}
        </p>
      </div>
      <div className={`estado-paso-real estado-${estado.toLowerCase()}`}>
        <small>Estado real</small>
        <strong>{etiquetasEstado[estado]}</strong>
      </div>
    </section>
  )
}
