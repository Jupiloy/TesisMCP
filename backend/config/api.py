from ninja import NinjaAPI
from ninja.security import django_auth

from thesis.services.errors import ErrorDominio
from thesis.api.projects import router as projects_router

api = NinjaAPI(title="TesisMCP", version="1.0.0", auth=django_auth)
api.add_router("/projects", projects_router)


@api.exception_handler(ErrorDominio)
def respuesta_error_dominio(request, exc: ErrorDominio):
    status = {
        "VALIDATION_ERROR": 400,
        "NOT_FOUND": 404,
        "PROJECT_ARCHIVED": 409,
        "VERSION_CONFLICT": 409,
        "SEARCH_UNAVAILABLE": 502,
        "PDF_UNREADABLE": 400,
        "OCR_UNAVAILABLE": 503,
        "OCR_FAILED": 422,
        "DOCX_UNREADABLE": 422,
        "DOCX_UNAVAILABLE": 503,
        "GROBID_UNAVAILABLE": 503,
        "GROBID_FAILED": 422,
        "EMBEDDING_UNAVAILABLE": 503,
        "REGISTRY_UNAVAILABLE": 502,
        "VALIDATION_SCHEMA_ERROR": 422,
        "RULE_WORD_COUNT_EXCEEDED": 400,
        "RULE_QUESTION_FORMAT": 400,
        "PREREQUISITE_LOCKED": 422,
        "ADVISOR_UNRESOLVED_COMMENTS": 412,
    }.get(exc.code, 500)
    return api.create_response(request, {"detail": f"{exc.code}: {exc.message}"}, status=status)
