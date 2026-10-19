import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from thesis.models import TokenAccesoMcp
from thesis.services.errors import ErrorDominio


def emitir_token(user, *, lifetime_hours: int = 24) -> str:
    if lifetime_hours < 1 or lifetime_hours > 720:
        raise ValueError("lifetime_hours fuera de rango")
    raw = secrets.token_urlsafe(48)
    TokenAccesoMcp.objects.create(
        user=user,
        token_hash=hashlib.sha256(raw.encode()).hexdigest(),
        expires_at=timezone.now() + timedelta(hours=lifetime_hours),
    )
    return raw


def usuario_desde_token(raw: str):
    if not raw:
        raise ErrorDominio("UNAUTHENTICATED", "Configura TESISMCP_MCP_TOKEN")
    digest = hashlib.sha256(raw.encode()).hexdigest()
    token = TokenAccesoMcp.objects.select_related("user").filter(
        token_hash=digest, revoked_at__isnull=True, expires_at__gt=timezone.now(),
        user__is_active=True,
    ).first()
    if token is None:
        raise ErrorDominio("UNAUTHENTICATED", "Token MCP inválido, vencido o revocado")
    return token.user
