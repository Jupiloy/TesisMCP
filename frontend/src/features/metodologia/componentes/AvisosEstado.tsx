interface AvisosEstadoProps {
  error?: string
  conflicto?: string
  confirmacion?: string
  alRecargar?: () => void
}

export default function AvisosEstado({
  error,
  conflicto,
  confirmacion,
  alRecargar,
}: AvisosEstadoProps) {
  if (!error && !conflicto && !confirmacion) return null

  const claseAviso = conflicto
    ? "aviso-conflicto"
    : error
      ? "aviso-error"
      : "aviso-exito"

  return (
    <div className={`aviso ${claseAviso}`} role="alert">
      <span>{conflicto || error || confirmacion}</span>
      {conflicto && alRecargar && (
        <button type="button" onClick={alRecargar}>
          Recargar versión actual
        </button>
      )}
    </div>
  )
}
