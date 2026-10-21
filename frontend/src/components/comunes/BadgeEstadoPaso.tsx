import { CheckCircle2, CircleDot, Lock } from "lucide-react"
import { cn } from "../../lib/utils"

interface BadgeEstadoPasoProps {
  estado: "COMPLETADO" | "DISPONIBLE" | "BLOQUEADO"
  tamano?: "sm" | "md"
  conIcono?: boolean
  className?: string
}

const configEstado = {
  COMPLETADO: {
    etiqueta: "Completado",
    icono: CheckCircle2,
    estilos: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  DISPONIBLE: {
    etiqueta: "Disponible",
    icono: CircleDot,
    estilos: "bg-blue-50 text-blue-700 border-blue-200",
  },
  BLOQUEADO: {
    etiqueta: "Bloqueado",
    icono: Lock,
    estilos: "bg-slate-100 text-slate-500 border-slate-200",
  },
} as const

export default function BadgeEstadoPaso({
  estado,
  tamano = "md",
  conIcono = true,
  className,
}: BadgeEstadoPasoProps) {
  const conf = configEstado[estado] ?? configEstado.DISPONIBLE
  const Icono = conf.icono

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-medium border rounded-md transition-colors",
        tamano === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs",
        conf.estilos,
        className,
      )}
    >
      {conIcono && <Icono className={tamano === "sm" ? "w-2.5 h-2.5" : "w-3.5 h-3.5"} />}
      <span>{conf.etiqueta}</span>
    </span>
  )
}
