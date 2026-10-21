export default function PanelAsistenteProximamente() {
  return (
    <section
      className="tarjeta-formulario panel-proximamente"
      aria-disabled="true"
    >
      <span className="eyebrow">ASISTENTE DE TESIS</span>
      <h2>Chat · Próximamente</h2>
      <p>Este panel todavía no está conectado a ningún agente.</p>
      <textarea
        disabled
        placeholder="Próximamente"
        aria-label="Chat próximamente"
      />
      <button
        className="button button-secondary"
        type="button"
        disabled
      >
        Próximamente
      </button>
    </section>
  )
}
