from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from thesis.services.autenticacion_mcp import emitir_token


class Command(BaseCommand):
    help = "Crea un token MCP local para un usuario activo; se muestra una sola vez."

    def add_arguments(self, parser):
        parser.add_argument("correo")
        parser.add_argument("--horas", type=int, default=24)

    def handle(self, *args, **options):
        usuario = get_user_model().objects.filter(email__iexact=options["correo"], is_active=True).first()
        if usuario is None:
            raise CommandError("No existe un usuario activo con ese correo")
        try:
            credencial = emitir_token(usuario, horas_vigencia=options["horas"])
        except ValueError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(credencial)
