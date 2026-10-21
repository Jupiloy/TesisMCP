import { type ReactNode } from "react"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { cn } from "../../lib/utils"

interface CampoTextoConContadorProps {
  id?: string
  etiqueta: string
  subetiqueta?: string
  tipo?: "input" | "textarea"
  valor: string
  alCambiar: (nuevoValor: string) => void
  longitudMin?: number
  longitudMax: number
  filas?: number
  placeholder?: string
  deshabilitado?: boolean
  obligatorio?: boolean
  ayuda?: string
  formatoInvalido?: boolean
  mensajeInvalido?: string
  accionDerecha?: ReactNode
}

export default function CampoTextoConContador({
  id,
  etiqueta,
  subetiqueta,
  tipo = "textarea",
  valor,
  alCambiar,
  longitudMin = 0,
  longitudMax,
  filas = 3,
  placeholder,
  deshabilitado = false,
  obligatorio = true,
  ayuda,
  formatoInvalido = false,
  mensajeInvalido,
  accionDerecha,
}: CampoTextoConContadorProps) {
  const longitudActual = valor.length
  const esDemasiadoCorto =
    longitudMin > 0 && longitudActual > 0 && longitudActual < longitudMin
  const esDemasiadoLargo = longitudActual > longitudMax

  const tieneError = formatoInvalido || esDemasiadoCorto || esDemasiadoLargo

  return (
    <div className="flex flex-col gap-1.5 my-3">
      <div className="flex items-center justify-between gap-3 text-xs">
        <label
          htmlFor={id}
          className="font-semibold text-slate-800 flex items-center gap-1.5"
        >
          {etiqueta}
          {obligatorio && <span className="text-red-500 font-bold">*</span>}
          {subetiqueta && (
            <span className="text-slate-400 font-normal text-[11px]">
              {subetiqueta}
            </span>
          )}
        </label>

        <div className="flex items-center gap-2">
          {accionDerecha}

          {/* Indicador de validación */}
          {longitudActual > 0 && (
            <span
              className={cn(
                "inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium transition-colors",
                tieneError
                  ? "bg-amber-50 text-amber-700 border border-amber-200"
                  : "bg-emerald-50 text-emerald-700 border border-emerald-200",
              )}
            >
              {tieneError ? (
                <>
                  <AlertCircle className="w-3 h-3 flex-none text-amber-600" />
                  {mensajeInvalido ??
                    (esDemasiadoCorto
                      ? `Mínimo ${longitudMin} caracteres`
                      : "Longitud excedida")}
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3 h-3 flex-none text-emerald-600" />
                  {longitudMin > 0 ? "Válido" : "Correcto"}
                </>
              )}
            </span>
          )}

          {/* Contador de caracteres */}
          <span
            className={cn(
              "text-[11px] font-mono",
              tieneError ? "text-amber-600 font-semibold" : "text-slate-400",
            )}
          >
            {longitudActual} / {longitudMax}
          </span>
        </div>
      </div>

      {tipo === "textarea" ? (
        <textarea
          id={id}
          rows={filas}
          minLength={longitudMin || undefined}
          maxLength={longitudMax}
          value={valor}
          onChange={(e) => alCambiar(e.target.value)}
          disabled={deshabilitado}
          placeholder={placeholder}
          required={obligatorio}
          className={cn(
            "w-full rounded-md border bg-white px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all resize-y",
            tieneError
              ? "border-amber-400 ring-1 ring-amber-300"
              : "border-slate-300 hover:border-slate-400",
            deshabilitado && "bg-slate-50 text-slate-500 cursor-not-allowed",
          )}
        />
      ) : (
        <input
          id={id}
          type="text"
          minLength={longitudMin || undefined}
          maxLength={longitudMax}
          value={valor}
          onChange={(e) => alCambiar(e.target.value)}
          disabled={deshabilitado}
          placeholder={placeholder}
          required={obligatorio}
          className={cn(
            "w-full h-9 rounded-md border bg-white px-3 text-xs text-slate-900 placeholder:text-slate-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all",
            tieneError
              ? "border-amber-400 ring-1 ring-amber-300"
              : "border-slate-300 hover:border-slate-400",
            deshabilitado && "bg-slate-50 text-slate-500 cursor-not-allowed",
          )}
        />
      )}

      {ayuda && <span className="text-[11px] text-slate-500">{ayuda}</span>}
    </div>
  )
}
