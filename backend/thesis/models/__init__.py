"""Importaciones públicas de los 15 modelos Django de TesisMCP (Avance Capítulos 1 al 3)."""

from .accounts import UserManager, User, McpAccessToken
from .projects import Project, ProjectParticipant
from .research import (
    ResearchProfile,
    ConsistencyRow,
    ResearchVariable,
    ConsistencyRowVariable,
    VariableDimension,
    Indicator,
)
from .chapters import StepProgress, Chapter, ChapterRevision, ReviewComment, ReviewEvent

# Alias en español para el código de aplicación.
GestorUsuarios = UserManager
Usuario = User
TokenAccesoMcp = McpAccessToken
Proyecto = Project
ParticipanteProyecto = ProjectParticipant
PerfilInvestigacion = ResearchProfile
FilaConsistencia = ConsistencyRow
VariableInvestigacion = ResearchVariable
VariableFilaConsistencia = ConsistencyRowVariable
DimensionVariable = VariableDimension
Indicador = Indicator
ProgresoPaso = StepProgress
Capitulo = Chapter
RevisionCapitulo = ChapterRevision
ComentarioRevision = ReviewComment
EventoRevision = ReviewEvent


COLUMNAS_FISICAS = {
    Usuario: {
        "password": "contrasena_hash",
        "last_login": "ultimo_acceso",
        "is_superuser": "es_superusuario",
        "first_name": "nombres",
        "last_name": "apellidos",
        "is_staff": "es_personal",
        "is_active": "esta_activo",
        "date_joined": "fecha_registro",
        "email": "correo",
        "display_name": "nombre_visible",
        "created_at": "creado_en",
    },
    TokenAccesoMcp: {
        "token_hash": "hash_token",
        "user": "usuario_id",
        "expires_at": "expira_en",
        "revoked_at": "revocado_en",
        "created_at": "creado_en",
    },
    Proyecto: {
        "name": "nombre",
        "title": "titulo",
        "status": "estado",
        "created_at": "creado_en",
        "updated_at": "actualizado_en",
    },
    ParticipanteProyecto: {
        "project": "proyecto_id",
        "user": "usuario_id",
        "role": "rol",
        "active": "activo",
        "joined_at": "incorporado_en",
        "left_at": "retirado_en",
    },
    PerfilInvestigacion: {
        "project": "proyecto_id",
        "approach": "enfoque",
        "topic": "tema",
        "ods_code": "codigo_ods",
        "unit_of_analysis": "unidad_analisis",
        "place": "lugar",
        "period_text": "periodo_texto",
        "problem_statement": "planteamiento_problema",
        "schema_version": "version_esquema",
        "lock_version": "version_bloqueo",
        "updated_at": "actualizado_en",
    },
    FilaConsistencia: {
        "project": "proyecto_id",
        "ordinal": "orden",
        "question_text": "texto_pregunta",
        "objective_text": "texto_objetivo",
        "hypothesis_text": "texto_hipotesis",
        "created_at": "creado_en",
        "updated_at": "actualizado_en",
    },
    VariableInvestigacion: {
        "project": "proyecto_id",
        "role": "rol",
        "name": "nombre",
        "conceptual_definition": "definicion_conceptual",
        "operational_definition": "definicion_operacional",
        "ordinal": "orden",
        "created_at": "creado_en",
        "updated_at": "actualizado_en",
    },
    VariableFilaConsistencia: {
        "consistency_row": "fila_consistencia_id",
        "variable": "variable_id",
        "created_at": "creado_en",
    },
    DimensionVariable: {
        "variable": "variable_id",
        "ordinal": "orden",
        "name": "nombre",
        "definition": "definicion",
    },
    Indicador: {
        "dimension": "dimension_id",
        "ordinal": "orden",
        "name": "nombre",
        "measurement_scale": "escala_medicion",
        "technique": "tecnica",
        "operational_rule": "regla_operacional",
    },
    ProgresoPaso: {
        "project": "proyecto_id",
        "step_code": "codigo_paso",
        "status": "estado",
        "output_json": "salida_json",
        "completed_at": "completado_en",
        "updated_at": "actualizado_en",
    },
    Capitulo: {
        "project": "proyecto_id",
        "number": "numero",
        "status": "estado",
        "approved_revision": "revision_aprobada_id",
        "approved_at": "aprobado_en",
        "created_at": "creado_en",
        "updated_at": "actualizado_en",
    },
    RevisionCapitulo: {
        "chapter": "capitulo_id",
        "revision_no": "numero_revision",
        "step_code": "codigo_paso",
        "idempotency_key": "clave_idempotencia",
        "content_md": "contenido_md",
        "content_sha256": "contenido_sha256",
        "created_by": "creado_por_id",
        "created_at": "creado_en",
    },
    ComentarioRevision: {
        "revision": "revision_id",
        "author": "autor_id",
        "start_cp": "inicio_caracter",
        "end_cp": "fin_caracter",
        "selected_text": "texto_seleccionado",
        "body": "contenido",
        "status": "estado",
        "resolved_by": "resuelto_por_id",
        "resolved_at": "resuelto_en",
        "created_at": "creado_en",
    },
    EventoRevision: {
        "chapter": "capitulo_id",
        "revision": "revision_id",
        "actor": "usuario_actor_id",
        "action": "accion",
        "reason": "motivo",
        "created_at": "creado_en",
    },
}


def _aplicar_nombres_fisicos() -> None:
    for modelo, columnas in COLUMNAS_FISICAS.items():
        for atributo, nombre_columna in columnas.items():
            campo = modelo._meta.get_field(atributo)
            campo.db_column = nombre_columna
            campo.column = nombre_columna

    tablas_intermedias = {
        "groups": (
            "tesis_usuario_grupo",
            "usuario_id",
            "grupo_id",
            "grupos",
            "Grupos a los que pertenece el usuario.",
        ),
        "user_permissions": (
            "tesis_usuario_permiso",
            "usuario_id",
            "permiso_id",
            "permisos del usuario",
            "Permisos específicos del usuario.",
        ),
    }
    for atributo, datos in tablas_intermedias.items():
        tabla, columna_usuario, columna_relacionada, nombre_visible, ayuda = datos
        campo = Usuario._meta.get_field(atributo)
        campo.db_table = tabla
        campo._verbose_name = nombre_visible
        campo.verbose_name = nombre_visible
        campo.help_text = ayuda
        tabla_intermedia = campo.remote_field.through
        tabla_intermedia._meta.db_table = tabla
        tabla_intermedia._meta.original_attrs["db_table"] = tabla
        campos_fk = [f for f in tabla_intermedia._meta.local_fields if f.many_to_one]
        for fk, columna in zip(campos_fk, (columna_usuario, columna_relacionada), strict=True):
            fk.db_column = columna
            fk.column = columna


_aplicar_nombres_fisicos()

__all__ = [
    "UserManager",
    "User",
    "McpAccessToken",
    "Project",
    "ProjectParticipant",
    "ResearchProfile",
    "ConsistencyRow",
    "ResearchVariable",
    "ConsistencyRowVariable",
    "VariableDimension",
    "Indicator",
    "StepProgress",
    "Chapter",
    "ChapterRevision",
    "ReviewComment",
    "ReviewEvent",
    "GestorUsuarios",
    "Usuario",
    "TokenAccesoMcp",
    "Proyecto",
    "ParticipanteProyecto",
    "PerfilInvestigacion",
    "FilaConsistencia",
    "VariableInvestigacion",
    "VariableFilaConsistencia",
    "DimensionVariable",
    "Indicador",
    "ProgresoPaso",
    "Capitulo",
    "RevisionCapitulo",
    "ComentarioRevision",
    "EventoRevision",
]
