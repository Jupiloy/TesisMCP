interface EditorContenidoNarrativoProps {
  contenido: string
  alCambiarContenido: (nuevoContenido: string) => void
  deshabilitado?: boolean
}

export default function EditorContenidoNarrativo({
  contenido,
  alCambiarContenido,
  deshabilitado = false,
}: EditorContenidoNarrativoProps) {
  return (
    <section className="tarjeta-formulario">
      <h2>Contenido narrativo</h2>
      <p>
        Se guarda como contenido_md junto con los datos estructurados del paso.
      </p>
      <label>
        Justificación y notas metodológicas
        <textarea
          className="editor-narrativo"
          required
          maxLength={200000}
          value={contenido}
          onChange={(evento) => alCambiarContenido(evento.target.value)}
          disabled={deshabilitado}
          placeholder="Redacta aquí el sustento metodológico en formato Markdown…"
        />
      </label>
    </section>
  )
}
