from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from thesis.services.mcp_auth import emitir_token


class Command(BaseCommand):
    help = "Crea un token MCP local para un usuario activo; se muestra una sola vez."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--hours", type=int, default=24)

    def handle(self, *args, **options):
        user = get_user_model().objects.filter(email__iexact=options["email"], is_active=True).first()
        if user is None:
            raise CommandError("No existe un usuario activo con ese correo")
        try:
            token = emitir_token(user, lifetime_hours=options["hours"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(token)
