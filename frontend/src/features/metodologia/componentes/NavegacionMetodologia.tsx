import {
  Check,
  ChevronDown,
  ChevronRight,
  Circle,
  LockKeyhole,
} from "lucide-react"
import type { EstadoProyecto, PasoCatalogo } from "../../../lib/api/cliente"

interface CapituloMetodologico {
  numero: number
  titulo: string
  codigos: readonly string[]
}

interface NavegacionMetodologiaProps {
  capitulos: readonly CapituloMetodologico[]
  capitulosAbiertos: number[]
  catalogo: PasoCatalogo[]
  proyecto: EstadoProyecto
  codigoPasoActivo: string
  alConmutarCapitulo: (numeroCapitulo: number) => void
  alSeleccionarPaso: (codigoPaso: string) => void
}

export default function NavegacionMetodologia({
  capitulos,
  capitulosAbiertos,
  catalogo,
  proyecto,
  codigoPasoActivo,
  alConmutarCapitulo,
  alSeleccionarPaso,
}: NavegacionMetodologiaProps) {
  const completados = proyecto.pasos.filter(
    (paso) => paso.estado === "COMPLETADO",
  ).length
  const total = proyecto.pasos.length
  const porcentaje = total > 0 ? Math.round((completados / total) * 100) : 0

  return (
    <>
      <div className="panel-tabs">
        <button className="active" type="button">
          Estructura <span>{total}</span>
        </button>
      </div>

      <nav className="outline-tree" aria-label="Estructura metodológica">
        <div className="outline-progress">
          <span>
            {completados} de {total} pasos completados
          </span>
          <div aria-label={`Avance ${porcentaje}%`}>
            <i style={{ width: `${porcentaje}%` }} />
          </div>
        </div>

        {capitulos.map((capitulo) => {
          const estaAbierto = capitulosAbiertos.includes(capitulo.numero)
          const pasos = capitulo.codigos.map((codigo) => ({
            codigo,
            catalogo: catalogo.find((paso) => paso.codigo === codigo),
            estado: proyecto.pasos.find((paso) => paso.codigo === codigo),
          }))

          return (
            <section className="outline-section" key={capitulo.numero}>
              <button
                className={`outline-chapter ${
                  pasos.some((paso) => paso.codigo === codigoPasoActivo)
                    ? "active"
                    : ""
                }`}
                type="button"
                onClick={() => alConmutarCapitulo(capitulo.numero)}
                aria-expanded={estaAbierto}
              >
                {estaAbierto ? (
                  <ChevronDown aria-hidden="true" size={14} />
                ) : (
                  <ChevronRight aria-hidden="true" size={14} />
                )}
                <span>
                  <b>{capitulo.titulo}</b>
                  <small>{pasos.length} pasos metodológicos</small>
                </span>
              </button>

              {estaAbierto && (
                <div className="outline-steps">
                  {pasos.map(({ codigo, catalogo: pasoCatalogo, estado }) => {
                    const estaActivo = codigo === codigoPasoActivo
                    const estaBloqueado = estado?.estado === "BLOQUEADO"
                    const estaCompletado = estado?.estado === "COMPLETADO"

                    return (
                      <button
                        className={`${estaActivo ? "current" : ""} ${
                          estaCompletado ? "done" : ""
                        }`}
                        type="button"
                        key={codigo}
                        disabled={estaBloqueado}
                        onClick={() => alSeleccionarPaso(codigo)}
                        aria-current={estaActivo ? "step" : undefined}
                        title={
                          estaBloqueado
                            ? `Completa ${(estado?.dependencias ?? []).join(", ") || "el paso anterior"}`
                            : (pasoCatalogo?.nombre ?? codigo)
                        }
                      >
                        <span aria-hidden="true">
                          {estaCompletado ? (
                            <Check size={10} />
                          ) : estaBloqueado ? (
                            <LockKeyhole size={9} />
                          ) : (
                            <Circle size={8} />
                          )}
                        </span>
                        <span className="outline-step-copy">
                          <b>{codigo}</b>
                          <small>{pasoCatalogo?.nombre ?? codigo}</small>
                        </span>
                      </button>
                    )
                  })}
                </div>
              )}
            </section>
          )
        })}
      </nav>
    </>
  )
}
