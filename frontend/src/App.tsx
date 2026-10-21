import RecorridoCapitulos from "./features/metodologia/RecorridoCapitulos"
import ErrorBoundary from "./components/comunes/ErrorBoundary"

export default function Aplicacion() {
  return (
    <ErrorBoundary nombreModulo="el recorrido metodológico">
      <RecorridoCapitulos />
    </ErrorBoundary>
  )
}
