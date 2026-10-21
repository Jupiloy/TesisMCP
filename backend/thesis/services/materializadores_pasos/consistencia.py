"""Reglas de delimitación, consistencia y operacionalización."""

from thesis.models import Proyecto, FilaConsistencia, VariableFilaConsistencia, Indicador, VariableInvestigacion, DimensionVariable
from thesis.services.errores import ErrorDominio

from .registro import ContextoEjecucionPaso, _obtener_salida_paso_completado, registrar_manejador_paso


def _sincronizar_filas_consistencia(
    proyecto: Proyecto,
    nombre_campo: str,
    valor_general: str,
    valores_especificos: list[str],
    truncar_sobrantes: bool = False,
) -> None:
    """Sincroniza la fila general y las específicas de la matriz de consistencia."""
    FilaConsistencia.objects.update_or_create(
        project=proyecto,
        ordinal=0,
        defaults={nombre_campo: valor_general},
    )
    for indice, valor_texto in enumerate(valores_especificos, start=1):
        FilaConsistencia.objects.update_or_create(
            project=proyecto,
            ordinal=indice,
            defaults={nombre_campo: valor_texto},
        )
    if truncar_sobrantes:
        VariableFilaConsistencia.objects.filter(
            consistency_row__project=proyecto,
            consistency_row__ordinal__gt=len(valores_especificos),
        ).delete()
        FilaConsistencia.objects.filter(
            project=proyecto,
            ordinal__gt=len(valores_especificos),
        ).delete()


@registrar_manejador_paso("P03")
def manejar_p03_ods(contexto: ContextoEjecucionPaso) -> None:
    contexto.perfil.ods_code = (
        f"ODS-{contexto.datos_validados['ods_principal_numero']:02d}:{contexto.datos_validados['meta_ods_especifica']}"
    )[:20]


@registrar_manejador_paso("P04")
def manejar_p04_titulo(contexto: ContextoEjecucionPaso) -> None:
    contexto.proyecto.title = contexto.datos_validados["titulo_oficial"]
    contexto.proyecto.save(update_fields=["title", "updated_at"])
    contexto.perfil.unit_of_analysis = contexto.datos_validados["unidad_analisis_confirmada"]
    contexto.perfil.place = contexto.datos_validados["lugar_confirmado"]
    contexto.perfil.period_text = str(contexto.datos_validados["periodo_confirmado"])


@registrar_manejador_paso("P06")
def manejar_p06_problema(contexto: ContextoEjecucionPaso) -> None:
    datos_p04 = _obtener_salida_paso_completado(contexto.proyecto, "P04")
    if any(
        valor.casefold() not in contexto.datos_validados["pregunta_general"].casefold()
        for valor in datos_p04.get("variables_confirmadas", [])
    ):
        raise ErrorDominio("FORMATO_PREGUNTA_INVALIDO", "La pregunta general debe mencionar las variables confirmadas")
    contexto.perfil.problem_statement = contexto.datos_validados["pregunta_general"]
    _sincronizar_filas_consistencia(
        proyecto=contexto.proyecto,
        nombre_campo="question_text",
        valor_general=contexto.datos_validados["pregunta_general"],
        valores_especificos=contexto.datos_validados.get("preguntas_especificas", []),
        truncar_sobrantes=True,
    )


@registrar_manejador_paso("P09")
def manejar_p09_objetivos(contexto: ContextoEjecucionPaso) -> None:
    datos_p04 = _obtener_salida_paso_completado(contexto.proyecto, "P04")
    if any(
        valor.casefold() not in contexto.datos_validados["objetivo_general"].casefold()
        for valor in datos_p04.get("variables_confirmadas", [])
    ):
        raise ErrorDominio(
            "INCONSISTENCIA_METODOLOGICA",
            "El objetivo general debe mencionar las variables confirmadas en P04",
        )
    datos_p06 = _obtener_salida_paso_completado(contexto.proyecto, "P06")
    preguntas_p06 = datos_p06.get("preguntas_especificas", [])
    objetivos_esp = contexto.datos_validados["objetivos_especificos"]
    if preguntas_p06 and len(objetivos_esp) != len(preguntas_p06):
        raise ErrorDominio(
            "INCONSISTENCIA_METODOLOGICA",
            f"El número de objetivos específicos ({len(objetivos_esp)}) "
            f"debe coincidir con las preguntas específicas de P06 ({len(preguntas_p06)})",
        )
    _sincronizar_filas_consistencia(
        proyecto=contexto.proyecto,
        nombre_campo="objective_text",
        valor_general=contexto.datos_validados["objetivo_general"],
        valores_especificos=objetivos_esp,
        truncar_sobrantes=True,
    )


@registrar_manejador_paso("P10")
def manejar_p10_preguntas(contexto: ContextoEjecucionPaso) -> None:
    datos_p09 = _obtener_salida_paso_completado(contexto.proyecto, "P09")
    objetivos_p09 = datos_p09.get("objetivos_especificos", [])
    preguntas_esp = contexto.datos_validados["preguntas_especificas"]
    if len(preguntas_esp) != len(objetivos_p09):
        raise ErrorDominio(
            "INCONSISTENCIA_METODOLOGICA",
            f"El número de preguntas específicas en P10 ({len(preguntas_esp)}) "
            f"debe coincidir con los objetivos específicos de P09 ({len(objetivos_p09)})",
        )
    _sincronizar_filas_consistencia(
        proyecto=contexto.proyecto,
        nombre_campo="question_text",
        valor_general=contexto.datos_validados["pregunta_general"],
        valores_especificos=preguntas_esp,
        truncar_sobrantes=False,
    )


@registrar_manejador_paso("P11")
def manejar_p11_hipotesis_y_variables(contexto: ContextoEjecucionPaso) -> None:
    datos_p09 = _obtener_salida_paso_completado(contexto.proyecto, "P09")
    objetivos_p09 = datos_p09.get("objetivos_especificos", [])
    hipotesis_esp = contexto.datos_validados["hipotesis_especificas"]
    if len(hipotesis_esp) != len(objetivos_p09):
        raise ErrorDominio(
            "INCONSISTENCIA_METODOLOGICA",
            f"El número de hipótesis específicas en P11 ({len(hipotesis_esp)}) "
            f"debe coincidir con los objetivos específicos de P09 ({len(objetivos_p09)})",
        )
    datos_p04 = _obtener_salida_paso_completado(contexto.proyecto, "P04")
    variables_declaradas = {
        contexto.datos_validados["variable_independiente"].casefold(),
        contexto.datos_validados["variable_dependiente"].casefold(),
    }
    for variable_confirmada in datos_p04.get("variables_confirmadas", []):
        if variable_confirmada.casefold() not in variables_declaradas:
            raise ErrorDominio(
                "INCONSISTENCIA_METODOLOGICA",
                f"La variable confirmada '{variable_confirmada}' en P04 debe figurar como variable en P11",
            )
    _sincronizar_filas_consistencia(
        proyecto=contexto.proyecto,
        nombre_campo="hypothesis_text",
        valor_general=contexto.datos_validados["hipotesis_general"],
        valores_especificos=hipotesis_esp,
        truncar_sobrantes=False,
    )
    var_ind, _ = VariableInvestigacion.objects.update_or_create(
        project=contexto.proyecto,
        ordinal=1,
        defaults={
            "role": VariableInvestigacion.Role.INDEPENDIENTE,
            "name": contexto.datos_validados["variable_independiente"],
        },
    )
    var_dep, _ = VariableInvestigacion.objects.update_or_create(
        project=contexto.proyecto,
        ordinal=2,
        defaults={
            "role": VariableInvestigacion.Role.DEPENDIENTE,
            "name": contexto.datos_validados["variable_dependiente"],
        },
    )
    VariableFilaConsistencia.objects.filter(variable__project=contexto.proyecto, variable__ordinal__gt=2).delete()
    VariableInvestigacion.objects.filter(project=contexto.proyecto, ordinal__gt=2).delete()
    for fila in FilaConsistencia.objects.filter(project=contexto.proyecto):
        VariableFilaConsistencia.objects.get_or_create(consistency_row=fila, variable=var_ind)
        VariableFilaConsistencia.objects.get_or_create(consistency_row=fila, variable=var_dep)


@registrar_manejador_paso("P12")
def manejar_p12_operacionalizacion(contexto: ContextoEjecucionPaso) -> None:
    variables_proyecto = list(VariableInvestigacion.objects.filter(project=contexto.proyecto).order_by("ordinal"))
    variables_por_nombre = {variable.name.casefold(): variable for variable in variables_proyecto}
    nombres_recibidos = {
        fila["variable"].casefold() for fila in contexto.datos_validados["matriz_operacionalizacion"]
    }
    if not variables_proyecto or nombres_recibidos != set(variables_por_nombre.keys()):
        raise ErrorDominio(
            "INCONSISTENCIA_METODOLOGICA",
            "Las variables en la matriz de operacionalización (P12) deben coincidir "
            "exactamente con las variables definidas en P11",
        )
    for fila in contexto.datos_validados["matriz_operacionalizacion"]:
        variable = variables_por_nombre[fila["variable"].casefold()]
        variable.conceptual_definition = fila["definicion_conceptual"]
        variable.operational_definition = fila["definicion_operacional"]
        variable.save(update_fields=["conceptual_definition", "operational_definition"])
        Indicador.objects.filter(dimension__variable=variable).delete()
        dimensiones = []
        for indice_dimension, nombre_dimension in enumerate(fila["dimensiones"], start=1):
            dimension, _ = DimensionVariable.objects.update_or_create(
                variable=variable,
                ordinal=indice_dimension,
                defaults={"name": nombre_dimension},
            )
            dimensiones.append(dimension)
        DimensionVariable.objects.filter(variable=variable, ordinal__gt=len(dimensiones)).delete()
        for indice_indicador, nombre_indicador in enumerate(fila["indicadores"]):
            dimension_destino = dimensiones[indice_indicador % len(dimensiones)]
            orden_dimension = (indice_indicador // len(dimensiones)) + 1
            Indicador.objects.create(
                dimension=dimension_destino,
                ordinal=orden_dimension,
                name=nombre_indicador,
                measurement_scale=fila["escala_medicion"],
            )
