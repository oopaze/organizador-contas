from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.domains.client import OAuthClient
from modules.ai.mcp.oauth.exceptions import InvalidRequestError
from modules.ai.mcp.oauth.use_cases.register_client import RegisterClientUseCase


class TestRegisterClientUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_repo = Mock()
        self.mock_token_gen = Mock()
        self.use_case = RegisterClientUseCase(
            client_repository=self.mock_repo,
            token_generator=self.mock_token_gen,
        )

    def test_creates_client_with_generated_id(self):
        self.mock_token_gen.generate_client_id.return_value = "mcp_new"
        self.mock_repo.create.return_value = OAuthClient(
            client_id="mcp_new", name="X", redirect_uris=["https://a/cb"],
            user_id=None, is_active=True,
        )
        result = self.use_case.execute(
            name="X", redirect_uris=["https://a/cb"],
        )
        self.assertEqual(result.client_id, "mcp_new")
        self.mock_repo.create.assert_called_once_with(
            client_id="mcp_new", name="X", redirect_uris=["https://a/cb"],
        )

    def test_rejects_empty_redirect_uris(self):
        with self.assertRaises(InvalidRequestError):
            self.use_case.execute(name="X", redirect_uris=[])

    def test_rejects_non_https_redirect_uri(self):
        with self.assertRaises(InvalidRequestError):
            self.use_case.execute(name="X", redirect_uris=["http://a/cb"])

    def test_allows_http_localhost(self):
        self.mock_token_gen.generate_client_id.return_value = "mcp_new"
        self.mock_repo.create.return_value = OAuthClient(
            client_id="mcp_new", name="X",
            redirect_uris=["http://localhost:5173/cb"],
            user_id=None, is_active=True,
        )
        result = self.use_case.execute(
            name="X", redirect_uris=["http://localhost:5173/cb"],
        )
        self.assertEqual(result.client_id, "mcp_new")
