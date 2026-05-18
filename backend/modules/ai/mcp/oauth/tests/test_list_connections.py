from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.domains.client import OAuthClient
from modules.ai.mcp.oauth.use_cases.list_connections import ListConnectionsUseCase


class TestListConnectionsUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_repo = Mock()
        self.use_case = ListConnectionsUseCase(client_repository=self.mock_repo)

    def test_lists_user_clients(self):
        self.mock_repo.list_for_user.return_value = [
            OAuthClient(client_id="mcp_a", name="A", redirect_uris=[], user_id=7, is_active=True),
            OAuthClient(client_id="mcp_b", name="B", redirect_uris=[], user_id=7, is_active=True),
        ]
        result = self.use_case.execute(user_id=7)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["client_id"], "mcp_a")
        self.assertEqual(result[0]["name"], "A")
