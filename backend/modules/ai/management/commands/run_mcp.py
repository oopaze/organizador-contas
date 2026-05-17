from django.core.management.base import BaseCommand

from modules.ai.mcp.server import run


class Command(BaseCommand):
    help = "Run the Poupix MCP server (stdio transport)."

    def handle(self, *args, **options):
        run()
