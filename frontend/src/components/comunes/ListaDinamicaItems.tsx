import { type ReactNode } from "react"
import { AlertCircle, CheckCircle2, Plus, Trash2 } from "lucide-react"
import { cn } from "../../lib/utils"

interface ListaDinamicaItemsProps {
  titulo: string
  subtitulo?: string
  etiquetaItem?: (indice: number) => string
  items: string[]
  alCambiarItems: (nuevos: string[]) => void
  minimo?: number
  maximo?: number
  longitudMin?: number
  longitudMax: number
  filas?: number
  placeholderItem?: string
  itemNuevoDefecto: string
  deshabilitado?: boolean
  validarItem?: (texto: string) => { esValido: boolean; mensaje: string }
  renderControlesItem?: (indice: number, item: string) => ReactNode
}

export default function ListaDinamicaItems({
  titulo,
  subtitulo,
  etiquetaItem,
  items,
  alCambiarItems,
  minimo = 2,
  maximo = 4,
  longitudMin = 0,
  longitudMax,
  filas = 2,
  placeholderItem = "Escriba aquí...",
  itemNuevoDefecto,
  deshabilitado = false,
  validarItem,
  renderControlesItem,
}: ListaDinamicaItemsProps) {
  function agregar() {
    if (deshabilitado || items.length >= maximo) return
    alCambiarItems([...items, itemNuevoDefecto])
  }

  function eliminar(indice: number) {
    if (deshabilitado || items.length <= minimo) return
    alCambiarItems(items.filter((_, i) => i !== indice))
  }

  function actualizar(indice: number, valor: string) {
    const copia = [...items]
    copia[indice] = valor
    alCambiarItems(copia)
  }

  return (
    <div className="flex flex-col gap-3 my-4">
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div>
          <h3 className="text-xs font-bold text-slate-800">{titulo}</h3>
          {subtitulo ? (
            <p className="text-[11px] text-slate-500">{subtitulo}</p>
          ) : (
            <p className="text-[11px] text-slate-400">
              Mínimo {minimo}, máximo {maximo} elementos (actual: {items.length})
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={agregar}
          disabled={deshabilitado || items.length >= maximo}
          className={cn(
            "inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md border transition-all",
            "border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100",
            (deshabilitado || items.length >= maximo) && "opacity-50 cursor-not-allowed hover:bg-blue-50",
          )}
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Agregar elemento</span>
        </button>
      </div>

      <div className="flex flex-col gap-2.5">
        {items.map((item, indice) => {
          const longitud = item.length
          const validacionExterna = validarItem?.(item)
          const esCorto = longitudMin > 0 && longitud > 0 && longitud < longitudMin
          const esLargo = longitud > longitudMax
          const tieneError = esCorto || esLargo || (validacionExterna && !validacionExterna.esValido)

          return (
            <div
              key={indice}
              className="flex flex-col gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-slate-300 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  {etiquetaItem ? etiquetaItem(indice) : `Elemento #${indice + 1}`}
                </span>

                <div className="flex items-center gap-2">
                  {validacionExterna && (
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium border",
                        validacionExterna.esValido
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-amber-50 text-amber-700 border-amber-200",
                      )}
                    >
                      {validacionExterna.esValido ? (
                        <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                      ) : (
                        <AlertCircle className="w-2.5 h-2.5 text-amber-600" />
                      )}
                      <span>{validacionExterna.mensaje}</span>
                    </span>
                  )}

                  <span
                    className={cn(
                      "text-[10px] font-mono",
                      tieneError ? "text-amber-600 font-semibold" : "text-slate-400",
                    )}
                  >
                    {longitud} / {longitudMax}
                  </span>

                  {items.length > minimo && (
                    <button
                      type="button"
                      onClick={() => eliminar(indice)}
                      disabled={deshabilitado}
                      title="Eliminar elemento"
                      className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {renderControlesItem && (
                <div className="pt-0.5 pb-1">{renderControlesItem(indice, item)}</div>
              )}

              <textarea
                rows={filas}
                minLength={longitudMin || undefined}
                maxLength={longitudMax}
                value={item}
                onChange={(e) => actualizar(indice, e.target.value)}
                disabled={deshabilitado}
                placeholder={placeholderItem}
                required
                className={cn(
                  "w-full rounded-md border bg-white px-2.5 py-1.5 text-xs text-slate-900 placeholder:text-slate-400",
                  "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all resize-y",
                  tieneError ? "border-amber-400 ring-1 ring-amber-300" : "border-slate-300 hover:border-slate-400",
                  deshabilitado && "bg-slate-50 text-slate-500 cursor-not-allowed",
                )}
              />
            </div>
          )
        })}
      </div>
    </div>
  )
}
