"""Contratos de salida de P01-P12 (Capítulos 1 al 3); validan forma, no veracidad científica."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SalidaEstricta(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TemaCandidato(SalidaEstricta):
    id: int = Field(ge=1, le=10)
    titulo_tentativo: str = Field(min_length=10, max_length=200)
    pros: list[str] = Field(min_length=1)
    contras: list[str] = Field(min_length=1)
    viabilidad_preliminar: str = Field(pattern="^(ALTA|MEDIA|BAJA)$")


class SalidaP01(SalidaEstricta):
    temas_propuestos: list[TemaCandidato] = Field(min_length=5, max_length=10)
    tema_preseleccionado_id: int | None = Field(default=None, ge=1, le=10)

    @model_validator(mode="after")
    def comprobar_identificadores(self):
        ids = [tema.id for tema in self.temas_propuestos]
        if len(set(ids)) != len(ids) or (self.tema_preseleccionado_id is not None and self.tema_preseleccionado_id not in ids):
            raise ValueError("Los identificadores de temas deben ser únicos y la preselección debe existir")
        return self


class CriterioEvaluacion(SalidaEstricta):
    acceso_a_datos: int = Field(ge=1, le=5)
    relevancia_profesional: int = Field(ge=1, le=5)
    brecha_conocimiento: int = Field(ge=1, le=5)
    recursos_disponibles: int = Field(ge=1, le=5)


class EvaluacionTema(SalidaEstricta):
    tema_id: int = Field(ge=1, le=10)
    titulo: str = Field(min_length=10)
    puntajes: CriterioEvaluacion
    puntaje_total: int = Field(ge=4, le=20)
    justificacion_eleccion: str = Field(min_length=20, max_length=500)

    @model_validator(mode="after")
    def comprobar_total(self):
        if self.puntaje_total != sum(self.puntajes.model_dump().values()):
            raise ValueError("El puntaje total no coincide con sus criterios")
        return self


class SalidaP02(SalidaEstricta):
    matriz_comparativa: list[EvaluacionTema] = Field(min_length=3, max_length=3)
    tema_ganador_id: int
    tema_ganador_titulo: str

    @model_validator(mode="after")
    def comprobar_ganador(self):
        ids = [item.tema_id for item in self.matriz_comparativa]
        winners = [item for item in self.matriz_comparativa if item.tema_id == self.tema_ganador_id]
        if (len(set(ids)) != 3 or len(winners) != 1 or winners[0].titulo != self.tema_ganador_titulo
                or winners[0].puntaje_total < max(item.puntaje_total for item in self.matriz_comparativa)):
            raise ValueError("El tema ganador debe existir exactamente en la matriz")
        return self


class SalidaP03(SalidaEstricta):
    ods_principal_numero: int = Field(ge=1, le=17)
    ods_principal_nombre: str = Field(min_length=5, max_length=100)
    meta_ods_especifica: str = Field(min_length=3, max_length=20)
    argumento_alineacion: str = Field(min_length=50, max_length=600)
    linea_utp_vinculada: str = Field(min_length=5, max_length=150)


class SalidaP04(SalidaEstricta):
    titulo_oficial: str = Field(min_length=15, max_length=250)
    conteo_palabras: int = Field(ge=1, le=20)
    variables_confirmadas: list[str] = Field(min_length=1, max_length=2)
    unidad_analisis_confirmada: str = Field(min_length=3)
    lugar_confirmado: str = Field(min_length=3)
    periodo_confirmado: int = Field(ge=2024, le=2030)

    @model_validator(mode="after")
    def comprobar_cantidad(self):
        if self.conteo_palabras != len(self.titulo_oficial.split()):
            raise ValueError("El conteo de palabras declarado no coincide con el título")
        title = self.titulo_oficial.casefold()
        components = [*self.variables_confirmadas, self.unidad_analisis_confirmada,
                      self.lugar_confirmado, str(self.periodo_confirmado)]
        if any(value.casefold() not in title for value in components):
            raise ValueError("El título debe mencionar variables, unidad, lugar y periodo confirmados")
        return self


class SalidaP05(SalidaEstricta):
    contenido_markdown: str = Field(min_length=500)
    num_parrafos: int = Field(ge=3)
    palabras_totales: int = Field(ge=250, le=1200)

    @model_validator(mode="after")
    def comprobar_cantidades(self):
        paragraphs = [value for value in self.contenido_markdown.split("\n\n") if value.strip()]
        if len(paragraphs) != self.num_parrafos or len(self.contenido_markdown.split()) != self.palabras_totales:
            raise ValueError("Los recuentos declarados no coinciden con el contenido")
        return self


class SalidaP06(SalidaEstricta):
    problema_central: str = Field(min_length=15, max_length=250)
    causas_directas: list[str] = Field(min_length=2, max_length=5)
    efectos_directos: list[str] = Field(min_length=2, max_length=5)
    pregunta_general: str = Field(min_length=20, max_length=250)
    preguntas_especificas: list[str] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def comprobar_preguntas(self):
        if not self.pregunta_general.startswith("¿") or not self.pregunta_general.endswith("?"):
            raise ValueError("La pregunta general requiere signos de interrogación")
        return self


class DimensionJustificacion(SalidaEstricta):
    dimension: str = Field(pattern="^(TEORICA|PRACTICA|METODOLOGICA|SOCIAL)$")
    argumento: str = Field(min_length=60, max_length=800)


class SalidaP07(SalidaEstricta):
    justificaciones: list[DimensionJustificacion] = Field(min_length=4, max_length=4)
    resumen_ejecutivo: str = Field(min_length=80, max_length=600)

    @model_validator(mode="after")
    def comprobar_dimensiones(self):
        if {item.dimension for item in self.justificaciones} != {"TEORICA", "PRACTICA", "METODOLOGICA", "SOCIAL"}:
            raise ValueError("Se requieren las cuatro dimensiones sin duplicados")
        return self


class SalidaP08(SalidaEstricta):
    brecha_detectada: str = Field(min_length=30, max_length=400)
    aporte_propuesto: str = Field(min_length=30, max_length=400)
    estado_evidencia: str = Field(default="PENDING_EVIDENCE", pattern="^PENDING_EVIDENCE$")


VERBOS_BLOOM_PERMITIDOS = {
    "DETERMINAR", "ANALIZAR", "EVALUAR", "DISEÑAR", "IMPLEMENTAR",
    "PROPONER", "IDENTIFICAR", "COMPARAR", "ESTABLECER", "EXAMINAR",
    "MEDIR", "DEMOSTRAR", "OPTIMIZAR", "DESARROLLAR", "MODELAR",
}


# --- Capítulo 3: Objetivos, Preguntas e Hipótesis ---

class SalidaP09(SalidaEstricta):
    objetivo_general: str = Field(min_length=15, max_length=250)
    objetivos_especificos: list[str] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def comprobar_bloom(self):
        first_word = self.objetivo_general.split()[0].upper().rstrip(":,;.")
        if first_word not in VERBOS_BLOOM_PERMITIDOS:
            raise ValueError(f"El objetivo general debe iniciar con un verbo de Bloom válido ('{first_word}')")
        for obj in self.objetivos_especificos:
            word = obj.split()[0].upper().rstrip(":,;.")
            if word not in VERBOS_BLOOM_PERMITIDOS:
                raise ValueError(f"Cada objetivo específico debe iniciar con un verbo de Bloom válido ('{word}')")
        return self


class SalidaP10(SalidaEstricta):
    pregunta_general: str = Field(min_length=15, max_length=250)
    preguntas_especificas: list[str] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def comprobar_signos_interrogacion(self):
        for q in [self.pregunta_general, *self.preguntas_especificas]:
            q_clean = q.strip()
            if not q_clean.startswith("¿") or not q_clean.endswith("?"):
                raise ValueError(f"La pregunta '{q}' debe iniciar con '¿' y terminar con '?'")
        return self


class SalidaP11(SalidaEstricta):
    tipo_investigacion: str = Field(pattern="^(APLICADA|BASICA|DESCRIPTIVA|CORRELACIONAL|EXPLICATIVA)$")
    hipotesis_general: str = Field(min_length=15, max_length=300)
    hipotesis_especificas: list[str] = Field(min_length=2, max_length=4)
    variable_independiente: str = Field(min_length=3, max_length=120)
    variable_dependiente: str = Field(min_length=3, max_length=120)


class FilaOperacionalizacion(SalidaEstricta):
    variable: str = Field(min_length=3, max_length=120)
    definicion_conceptual: str = Field(min_length=20, max_length=400)
    definicion_operacional: str = Field(min_length=20, max_length=400)
    dimensiones: list[str] = Field(min_length=1, max_length=6)
    indicadores: list[str] = Field(min_length=1, max_length=10)
    escala_medicion: str = Field(pattern="^(NOMINAL|ORDINAL|INTERVALO|RAZON)$")


class SalidaP12(SalidaEstricta):
    matriz_operacionalizacion: list[FilaOperacionalizacion] = Field(min_length=1, max_length=4)


CONTRATOS = {
    "P01": SalidaP01,
    "P02": SalidaP02,
    "P03": SalidaP03,
    "P04": SalidaP04,
    "P05": SalidaP05,
    "P06": SalidaP06,
    "P07": SalidaP07,
    "P08": SalidaP08,
    "P09": SalidaP09,
    "P10": SalidaP10,
    "P11": SalidaP11,
    "P12": SalidaP12,
}
