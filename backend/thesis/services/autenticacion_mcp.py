import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from thesis.models import TokenAccesoMcp
from thesis.services.errores import ErrorDominio


def emitir_token(usuario, *, horas_vigencia: int = 24) -> str:
    if horas_vigencia < 1 or horas_vigencia > 720:
        raise ValueError("horas_vigencia fuera de rango")
    credencial_plana = secrets.token_urlsafe(48)
    TokenAccesoMcp.objects.create(
        user=usuario,
        token_hash=hashlib.sha256(credencial_plana.encode()).hexdigest(),
        expires_at=timezone.now() + timedelta(hours=horas_vigencia),
    )
    return credencial_plana


def usuario_desde_token(credencial_plana: str):
    if not credencial_plana:
        raise ErrorDominio("NO_AUTENTICADO", "Configura TESISMCP_MCP_TOKEN")
    resumen = hashlib.sha256(credencial_plana.encode()).hexdigest()
    credencial = TokenAccesoMcp.objects.select_related("user").filter(
        token_hash=resumen, revoked_at__isnull=True, expires_at__gt=timezone.now(),
        user__is_active=True,
    ).first()
    if credencial is None:
        raise ErrorDominio("NO_AUTENTICADO", "Token MCP inválido, vencido o revocado")
    return credencial.user
