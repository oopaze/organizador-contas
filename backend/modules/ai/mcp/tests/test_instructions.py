from django.test import SimpleTestCase

from modules.ai.mcp import instructions
from modules.ai.mcp.http import views


class TestServerInstructions(SimpleTestCase):
    def test_initialize_includes_instructions_and_version(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"}, user_id=1
        )

        result = response["result"]
        self.assertEqual(result["serverInfo"]["version"], "0.4.0")
        self.assertEqual(result["instructions"], instructions.SERVER_INSTRUCTIONS)
        self.assertIn("fatura", instructions.SERVER_INSTRUCTIONS.lower())
