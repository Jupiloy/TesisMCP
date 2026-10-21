import { Component, type ErrorInfo, type ReactNode } from "react"

export interface PropiedadesErrorBoundary {
  children: ReactNode
  nombreModulo?: string
  alRestablecer?: () => void
  alReintentar?: () => void
}

interface EstadoErrorBoundary {
  tieneError: boolean
  error: Error | null
  informacionError: ErrorInfo | null
}

export default class ErrorBoundary extends Component<
  PropiedadesErrorBoundary,
  EstadoErrorBoundary
> {
  constructor(props: PropiedadesErrorBoundary) {
    super(props)
    this.state = {
      tieneError: false,
      error: null,
      informacionError: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<EstadoErrorBoundary> {
    return { tieneError: true, error }
  }

  componentDidCatch(error: Error, informacionError: ErrorInfo) {
    this.setState({ informacionError })
    // eslint-disable-next-line no-console
    console.error(
      `[ErrorBoundary: ${this.props.nombreModulo ?? "General"}]`,
      error,
      informacionError,
    )
  }

  manejarReintentar = () => {
    this.setState({ tieneError: false, error: null, informacionError: null })
    if (this.props.alReintentar) {
      this.props.alReintentar()
    }
  }

  manejarRestablecer = () => {
    this.setState({ tieneError: false, error: null, informacionError: null })
    if (this.props.alRestablecer) {
      this.props.alRestablecer()
    }
  }

  render() {
    if (this.state.tieneError) {
      const nombre = this.props.nombreModulo ?? "esta sección"
      return (
        <section
          className="tarjeta-formulario tarjeta-error-boundary"
          role="alert"
          style={{
            border: "1px solid #dc2626",
            background: "#fff5f5",
            padding: "1.5rem",
            borderRadius: "0.5rem",
            margin: "1rem 0",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "1.5rem" }} aria-hidden="true">
              ⚠️
            </span>
            <div>
              <h3 style={{ margin: 0, color: "#991b1b", fontSize: "1.1rem" }}>
                Error al renderizar {nombre}
              </h3>
              <p style={{ margin: "0.25rem 0 0 0", color: "#7f1d1d", fontSize: "0.875rem" }}>
                Se detectó una discrepancia en los datos de este paso. El sistema previno una pantalla blanca.
              </p>
            </div>
          </div>

          <div
            style={{
              background: "#ffffff",
              border: "1px solid #fecaca",
              borderRadius: "0.375rem",
              padding: "0.75rem",
              marginBottom: "1rem",
              fontSize: "0.8125rem",
              fontFamily: "monospace",
              color: "#b91c1c",
              overflowX: "auto",
              maxHeight: "150px",
            }}
          >
            {this.state.error?.message ?? "Error desconocido de renderizado"}
          </div>

          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <button
              type="button"
              className="button button-primary"
              onClick={this.manejarReintentar}
            >
              🔄 Reintentar carga
            </button>
            {this.props.alRestablecer && (
              <button
                type="button"
                className="button button-outline"
                onClick={this.manejarRestablecer}
              >
                📋 Restablecer a plantilla inicial del paso
              </button>
            )}
          </div>
        </section>
      )
    }

    return this.props.children
  }
}
