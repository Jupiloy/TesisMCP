from ninja import NinjaAPI
from ninja.errors import AuthenticationError, AuthorizationError, HttpError, ValidationError
from ninja.security import django_auth
from django.middleware.csrf import get_token
from django.http import JsonResponse

from thesis.services.errores import ErrorDominio
from thesis.api.proyectos import router as router_proyectos
from thesis.services.revisiones import panel_asesor
from thesis.services.contratos_pasos import CONTRATOS
from thesis.catalogo_pasos import CATALOGO_PASOS

api = NinjaAPI(title="TesisMCP", version="1.0.0", auth=django_auth)
api.add_router("/proyectos", router_proyectos)


@api.get("/sesion/actual", tags=["Sesión"])
def sesion_actual(request):
    get_token(request)
    return {
        "correo": request.user.email,
        "nombre_visible": request.user.display_name,
    }


@api.get("/metodologia/catalogo", tags=["Metodología"])
def catalogo_metodologico(request):
    codigos = list(CATALOGO_PASOS)
    return [
        {
            "codigo": codigo,
            "capitulo": datos["capitulo"],
            "nombre": datos["nombre"],
            "objetivo": datos["objetivo"],
            "entradas_requeridas": datos["entradas_requeridas"],
            "dependencias": [codigos[indice - 1]] if indice else [],
            "esquema_salida": CONTRATOS[codigo].model_json_schema(),
        }
        for indice, (codigo, datos) in enumerate(CATALOGO_PASOS.items())
    ]


@api.get("/asesor/panel", tags=["Asesor"])
def obtener_panel_asesor(request):
    return panel_asesor(request.user)


@api.exception_handler(ErrorDominio)
def respuesta_error_dominio(request, exc: ErrorDominio):
    estado_http = {
        "ERROR_VALIDACION": 400,
        "NO_ENCONTRADO": 404,
        "PROYECTO_ARCHIVADO": 409,
        "CONFLICTO_VERSION": 409,
        "BUSQUEDA_NO_DISPONIBLE": 502,
        "PDF_ILEGIBLE": 400,
        "OCR_NO_DISPONIBLE": 503,
        "FALLO_OCR": 422,
        "DOCX_ILEGIBLE": 422,
        "DOCX_NO_DISPONIBLE": 503,
        "GROBID_NO_DISPONIBLE": 503,
        "FALLO_GROBID": 422,
        "VECTORIZACION_NO_DISPONIBLE": 503,
        "REGISTRO_NO_DISPONIBLE": 502,
        "ERROR_ESQUEMA_VALIDACION": 422,
        "LIMITE_PALABRAS_EXCEDIDO": 400,
        "FORMATO_PREGUNTA_INVALIDO": 400,
        "PRERREQUISITO_BLOQUEADO": 422,
        "INCONSISTENCIA_METODOLOGICA": 422,
        "OBSERVACIONES_ASESOR_SIN_RESOLVER": 412,
        "NO_AUTENTICADO": 401,
    }.get(exc.codigo, 500)
    return api.create_response(
        request,
        {"codigo": exc.codigo, "mensaje": exc.mensaje, "detalle": f"{exc.codigo}: {exc.mensaje}"},
        status=estado_http,
    )


def _respuesta_error_publico(request, *, codigo: str, mensaje: str, detalle, estado_http: int):
    return api.create_response(
        request,
        {"codigo": codigo, "mensaje": mensaje, "detalle": detalle},
        status=estado_http,
    )


@api.exception_handler(AuthenticationError)
def respuesta_no_autenticado(request, error: AuthenticationError):
    return _respuesta_error_publico(
        request,
        codigo="NO_AUTENTICADO",
        mensaje="Se requiere una sesión autenticada",
        detalle="La solicitud no contiene una sesión válida",
        estado_http=401,
    )


@api.exception_handler(AuthorizationError)
def respuesta_no_autorizado(request, error: AuthorizationError):
    return _respuesta_error_publico(
        request,
        codigo="NO_AUTORIZADO",
        mensaje="La operación no está autorizada",
        detalle="El usuario autenticado no tiene permisos para esta operación",
        estado_http=403,
    )


@api.exception_handler(ValidationError)
def respuesta_validacion_entrada(request, error: ValidationError):
    ubicaciones = []
    for fallo in error.errors:
        ubicacion = ".".join(str(segmento) for segmento in fallo.get("loc", []))
        if ubicacion:
            ubicaciones.append(ubicacion)
    detalle = "Campos inválidos: " + ", ".join(sorted(set(ubicaciones))) if ubicaciones else "Entrada inválida"
    return _respuesta_error_publico(
        request,
        codigo="ERROR_VALIDACION",
        mensaje="La entrada no cumple el contrato requerido",
        detalle=detalle,
        estado_http=422,
    )


@api.exception_handler(HttpError)
def respuesta_error_http(request, error: HttpError):
    return _respuesta_error_publico(
        request,
        codigo="ERROR_HTTP",
        mensaje="La solicitud HTTP no pudo procesarse",
        detalle=str(error),
        estado_http=error.status_code,
    )


def respuesta_error_csrf(request, reason=""):
    """Normaliza el rechazo CSRF del middleware al contrato público en español."""
    return JsonResponse(
        {
            "codigo": "CSRF_INVALIDO",
            "mensaje": "La verificación CSRF falló",
            "detalle": "Falta un token CSRF válido para esta operación",
        },
        status=403,
    )
