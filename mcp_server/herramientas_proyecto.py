"""Adaptadores MCP para los Capítulos 1 al 3 y exploración inicial: sus reglas viven en servicios."""

import json
from typing import Any
from uuid import UUID

from mcp.server.mcpserver.exceptions import ToolError

from mcp_server.puente_django import usuario_actual, configurar_django


def _error_publico(codigo: str, mensaje: str, detalle: str) -> ToolError:
    """Codifica el error de herramienta con el mismo contrato público que HTTP."""
    return ToolError(json.dumps(
        {"codigo": codigo, "mensaje": mensaje, "detalle": detalle},
        ensure_ascii=False,
    ))


def _invocar(operacion, *args, **kwargs):
    from django.db import connections
    from thesis.services.errores import ErrorDominio

    try:
        return operacion(usuario_actual(), *args, **kwargs)
    except ErrorDominio as exc:
        raise _error_publico(exc.codigo, exc.mensaje, f"{exc.codigo}: {exc.mensaje}") from exc
    finally:
        connections.close_all()


def _uuid_proyecto(id_proyecto: str) -> UUID:
    try:
        return UUID(id_proyecto)
    except ValueError as error:
        raise _error_publico(
            "ERROR_VALIDACION",
            "id_proyecto debe ser UUID",
            "El identificador recibido no tiene formato UUID",
        ) from error


def registrar_herramientas_proyecto(app) -> None:
    configurar_django()
    from thesis.services.descubrimiento import buscar_semantic_scholar_servicio
    from thesis.services.descubrimiento_peru import buscar_antecedentes_peru_servicio
    from thesis.services.exploracion import explorar_idea_servicio
    from thesis.services.proyectos import crear_proyecto_servicio, obtener_estado_proyecto, registrar_idea_servicio
    from thesis.services.revisiones import (
        agregar_comentario_servicio,
        asignar_asesor_servicio,
        decidir_capitulo_servicio,
        listar_comentarios_servicio,
        resolver_comentario_servicio,
    )
    from thesis.services.pasos import obtener_capitulo_servicio, guardar_paso_servicio, enviar_capitulo_servicio

    @app.tool()
    def crear_proyecto(nombre: str, titulo: str | None = None) -> dict[str, Any]:
        """Crea un proyecto para el usuario autenticado del cliente MCP."""
        def operacion(usuario):
            proyecto = crear_proyecto_servicio(usuario, nombre, titulo)
            return obtener_estado_proyecto(usuario, proyecto.id)

        return _invocar(operacion)

    @app.tool()
    def obtener_estado(id_proyecto: str) -> dict[str, Any]:
        """Consulta el estado de un proyecto al que pertenece el usuario."""
        return _invocar(obtener_estado_proyecto, _uuid_proyecto(id_proyecto))

    @app.tool()
    def registrar_idea(id_proyecto: str, descripcion: str, version_esperada: int) -> dict[str, Any]:
        """Guarda una idea provisional confirmada por el tesista, con control de versión."""
        return _invocar(registrar_idea_servicio, _uuid_proyecto(id_proyecto), descripcion, version_esperada)

    @app.tool()
    def explorar_idea(id_proyecto: str) -> dict[str, Any]:
        """Busca literatura sobre la idea guardada; devuelve solo metadatos, no resultados demostrados."""
        return _invocar(explorar_idea_servicio, _uuid_proyecto(id_proyecto))

    @app.tool()
    def buscar_semantic_scholar(id_proyecto: str, consulta: str, limite: int = 5) -> dict[str, Any]:
        """Busca metadatos en Semantic Scholar; no inspecciona ni verifica el texto completo."""
        return _invocar(buscar_semantic_scholar_servicio, _uuid_proyecto(id_proyecto), consulta, limite)

    @app.tool()
    def buscar_antecedentes_peru(
        id_proyecto: str,
        consulta: str,
        filtro_alcance: str = "todos",
        incluir_articulos: bool = True,
        limite: int = 5,
    ) -> dict[str, Any]:
        """Busca tesis en ALICIA y artículos con filiación peruana; no acredita revisión por pares ni inspección del PDF."""
        return _invocar(
            buscar_antecedentes_peru_servicio,
            _uuid_proyecto(id_proyecto),
            consulta,
            filtro_alcance=filtro_alcance,
            incluir_articulos=incluir_articulos,
            limite=limite,
        )

    @app.tool()
    def guardar_paso(
        id_proyecto: str,
        codigo_paso: str,
        contenido_md: str,
        datos_salida: dict[str, Any],
        version_esperada: int,
        clave_idempotencia: str,
    ) -> dict[str, Any]:
        """Valida P01-P12 (Capítulos 1 al 3) y guarda una revisión completa confirmada por el tesista."""
        return _invocar(
            guardar_paso_servicio,
            _uuid_proyecto(id_proyecto),
            codigo_paso,
            contenido_md,
            datos_salida,
            version_esperada,
            clave_idempotencia,
        )

    @app.tool()
    def consultar_capitulo(id_proyecto: str, numero_capitulo: int) -> dict[str, Any]:
        """Lee progreso y revisión vigente de un capítulo autorizado (1 al 3)."""
        return _invocar(obtener_capitulo_servicio, _uuid_proyecto(id_proyecto), numero_capitulo)

    @app.tool()
    def enviar_capitulo(id_proyecto: str, numero_capitulo: int) -> dict[str, Any]:
        """Envía al asesor un capítulo (1 al 3) cuyos pasos están completos."""
        return _invocar(enviar_capitulo_servicio, _uuid_proyecto(id_proyecto), numero_capitulo)

    @app.tool()
    def asignar_asesor(id_proyecto: str, correo: str) -> dict[str, Any]:
        """Asigna un usuario existente como asesor activo del proyecto del tesista."""
        return _invocar(asignar_asesor_servicio, _uuid_proyecto(id_proyecto), correo)

    @app.tool()
    def consultar_observaciones(id_proyecto: str, numero_capitulo: int) -> list[dict[str, Any]]:
        """Lista comentarios anclados a revisiones de un capítulo autorizado."""
        return _invocar(listar_comentarios_servicio, _uuid_proyecto(id_proyecto), numero_capitulo)

    @app.tool()
    def observar_fragmento(
        id_proyecto: str,
        numero_capitulo: int,
        inicio_caracter: int,
        fin_caracter: int,
        texto_seleccionado: str,
        contenido: str,
    ) -> dict[str, Any]:
        """El asesor comenta un fragmento exacto de la revisión vigente."""
        return _invocar(
            agregar_comentario_servicio,
            _uuid_proyecto(id_proyecto),
            numero_capitulo,
            inicio_caracter,
            fin_caracter,
            texto_seleccionado,
            contenido,
        )

    @app.tool()
    def decidir_capitulo(id_proyecto: str, numero_capitulo: int, accion: str, motivo: str = "") -> dict[str, Any]:
        """El asesor solicita cambios, aprueba o reabre un capítulo con las guardas del dominio."""
        return _invocar(decidir_capitulo_servicio, _uuid_proyecto(id_proyecto), numero_capitulo, accion, motivo)

    @app.tool()
    def resolver_observacion(id_proyecto: str, id_comentario: int) -> dict[str, Any]:
        """El asesor marca como resuelta una observación del proyecto."""
        return _invocar(resolver_comentario_servicio, _uuid_proyecto(id_proyecto), id_comentario)
