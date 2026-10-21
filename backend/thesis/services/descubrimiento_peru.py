"""Servicio de búsqueda y clasificación de antecedentes científicos nacionales y locales (Perú)."""

from typing import Any

from thesis.integrations.alicia import buscar_tesis_alicia
from thesis.integrations.articulos_peru import buscar_articulos_afiliacion_peru
from thesis.models import PerfilInvestigacion
from thesis.services.acceso import requerir_proyecto
from thesis.services.errores import ErrorDominio
from thesis.services.geografia import AlcanceGeografico, _contiene_termino, _quitar_tildes, resolver_alcance_geografico


def _clasificar_localidad(elemento: dict, alcance: AlcanceGeografico) -> tuple[bool, str]:
    """Evalúa de forma determinista si un registro califica como local y explica la razón."""
    titulo_limpio = _quitar_tildes(elemento.get("titulo") or "")
    resumen_limpio = _quitar_tildes(elemento.get("resumen") or "")
    texto_combinado = f"{titulo_limpio} {resumen_limpio}"

    # 1. Comprobar si la institución es una universidad local de la zona (por acrónimo o nombre de región)
    institucion_limpia = _quitar_tildes(elemento.get("institucion") or "")
    region_limpia = _quitar_tildes(alcance.region)
    if alcance.palabras_coincidencia and _contiene_termino(institucion_limpia, region_limpia):
        return True, f"LOCAL_POR_INSTITUCION: {elemento.get('institucion')}"

    for institucion_local in alcance.instituciones_locales:
        if _contiene_termino(institucion_limpia, institucion_local):
            return True, f"LOCAL_POR_INSTITUCION: {elemento.get('institucion')}"

    # 2. Comprobar si el objeto de estudio, población o empresa está en la localidad
    for palabra in alcance.palabras_coincidencia:
        if _contiene_termino(texto_combinado, palabra) or _contiene_termino(institucion_limpia, palabra):
            return True, f"LOCAL_POR_OBJETO_ESTUDIO: Coincidencia geográfica con '{palabra}'"

    return False, "NACIONAL: Ámbito general Perú"


def buscar_antecedentes_peru_servicio(
    usuario,
    id_proyecto,
    consulta: str,
    filtro_alcance: str = "todos",
    incluir_articulos: bool = True,
    limite: int = 5,
) -> dict[str, Any]:
    """Busca tesis en ALICIA y artículos con filiación peruana, sin certificar arbitraje."""
    proyecto = requerir_proyecto(usuario, id_proyecto)
    consulta = consulta.strip()
    if not consulta:
        raise ErrorDominio("ERROR_VALIDACION", "La consulta de búsqueda no puede estar vacía")
    if filtro_alcance not in ("todos", "locales", "nacionales"):
        raise ErrorDominio("ERROR_VALIDACION", "filtro_alcance debe ser 'todos', 'locales' o 'nacionales'")
    if not 1 <= limite <= 20:
        raise ErrorDominio("ERROR_VALIDACION", "limite debe estar entre 1 y 20")

    perfil = PerfilInvestigacion.objects.filter(project=proyecto).first()
    lugar = perfil.place if perfil else None
    alcance = resolver_alcance_geografico(lugar)
    if filtro_alcance == "locales" and not alcance.palabras_coincidencia:
        raise ErrorDominio("ERROR_VALIDACION", "Configura el lugar del proyecto antes de buscar antecedentes locales")

    candidatos: list[dict] = []
    errores_proveedor: list[str] = []
    proveedores_exitosos = 0

    # 1. Búsqueda local orientada a la región
    if filtro_alcance in ("todos", "locales") and alcance.palabras_coincidencia:
        try:
            consulta_local = f"{consulta} {alcance.region}"
            tesis_locales = buscar_tesis_alicia(consulta_local, limite=limite)
            candidatos.extend(tesis_locales)
            proveedores_exitosos += 1
        except ErrorDominio:
            errores_proveedor.append("ALICIA_LOCAL")

    # 2. Búsqueda nacional en ALICIA
    if filtro_alcance in ("todos", "nacionales") or len(candidatos) < limite:
        try:
            tesis_nacionales = buscar_tesis_alicia(consulta, limite=limite)
            candidatos.extend(tesis_nacionales)
            proveedores_exitosos += 1
        except ErrorDominio:
            errores_proveedor.append("ALICIA_NACIONAL")

    # 3. Artículos con filiación peruana; la revisión por pares queda sin acreditar.
    if incluir_articulos:
        try:
            articulos = buscar_articulos_afiliacion_peru(consulta, limite=min(limite, 5))
            candidatos.extend(articulos)
            proveedores_exitosos += 1
        except ErrorDominio:
            errores_proveedor.append("OPENALEX_PERU")
    if not proveedores_exitosos:
        raise ErrorDominio("BUSQUEDA_NO_DISPONIBLE", "No se pudo consultar ningún proveedor de antecedentes peruanos")

    # Clasificación y deduplicación por título normalizado
    titulos_vistos = set()
    resultados_clasificados = []
    for elemento in candidatos:
        clave_titulo = (elemento.get("titulo") or "").strip().lower()
        if not clave_titulo or clave_titulo in titulos_vistos:
            continue
        titulos_vistos.add(clave_titulo)

        es_local, justificacion = _clasificar_localidad(elemento, alcance)
        elemento["es_local"] = es_local
        elemento["justificacion_local"] = justificacion
        elemento["region_evaluada"] = alcance.region

        # Filtrar según la opción seleccionada
        if filtro_alcance == "locales" and not es_local:
            continue
        if filtro_alcance == "nacionales" and es_local:
            continue

        resultados_clasificados.append(elemento)

    # Ordenar: si es "todos", priorizar los locales primero, luego por año descendente
    def _clave_ordenamiento(elemento_orden: dict):
        peso_local = 0 if elemento_orden.get("es_local") else 1
        peso_anio = -(elemento_orden.get("anio_publicacion") or 0)
        return (peso_local, peso_anio)

    resultados_clasificados.sort(key=_clave_ordenamiento)
    lista_final = resultados_clasificados[:limite]

    return {
        "id_proyecto": str(proyecto.id),
        "consulta": consulta,
        "region_detectada": alcance.region,
        "filtro_alcance": filtro_alcance,
        "total_encontrados": len(lista_final),
        "resultados": lista_final,
        "fuentes_no_disponibles": errores_proveedor,
        "nivel_verificacion": "SOLO_METADATOS",
        "texto_completo_inspeccionado": False,
    }
