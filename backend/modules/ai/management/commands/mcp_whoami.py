from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Print the user_id for an email — used when configuring mcp.json."

    def add_arguments(self, parser):
        parser.add_argument("email", help="The user's email address")

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(email=options["email"])
        except User.DoesNotExist as exc:
            raise CommandError(f"No user with email {options['email']!r}") from exc
        self.stdout.write(self.style.SUCCESS(
            f"user_id = {user.id}  (use this as POUPIX_MCP_USER_ID)"
        ))
