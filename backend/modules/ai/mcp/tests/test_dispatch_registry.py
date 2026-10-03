from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidDateError
from modules.ai.mcp.tools import HANDLERS, TOOLS, dispatch_tool


class TestDispatchRegistry(SimpleTestCase):
    def test_every_tool_has_a_handler(self):
        self.assertEqual(
            sorted(tool["name"] for tool in TOOLS),
            sorted(HANDLERS),
        )

    def test_unknown_tool_lists_available(self):
        result = dispatch_tool("nao_existe", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "UNKNOWN_TOOL")
        self.assertIn("list_transactions", result["error"]["available_tools"])

    def test_mcp_error_maps_stable_code(self):
        def boom(arguments, container, user_id):
            raise InvalidDateError("data inválida")

        with patch.dict(HANDLERS, {"boom": boom}):
            result = dispatch_tool("boom", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "INVALID_DATE")
        self.assertEqual(result["error"]["message"], "data inválida")

    def test_wraps_unexpected_errors(self):
        def boom(arguments, container, user_id):
            raise Exception("boom")

        with patch.dict(HANDLERS, {"boom": boom}):
            result = dispatch_tool("boom", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "TOOL_ERROR")
