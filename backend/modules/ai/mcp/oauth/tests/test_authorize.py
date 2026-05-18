from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.domains.client import OAuthClient
from modules.ai.mcp.oauth.domains.auth_code import AuthorizationCode
from modules.ai.mcp.oauth.exceptions import (
    InvalidClientError, InvalidRequestError,
)
from modules.ai.mcp.oauth.use_cases.authorize import AuthorizeUseCase


class TestAuthorizeUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_client_repo = Mock()
        self.mock_code_repo = Mock()
        self.mock_token_gen = Mock()
        self.use_case = AuthorizeUseCase(
            client_repository=self.mock_client_repo,
            auth_code_repository=self.mock_code_repo,
            token_generator=self.mock_token_gen,
        )

    def _client(self, redirect_uris=None):
        return OAuthClient(
            client_id="mcp_x", name="X",
            redirect_uris=redirect_uris or ["https://a/cb"],
            user_id=None, is_active=True,
        )

    def test_issues_code_and_assigns_user(self):
        self.mock_client_repo.get_by_client_id.return_value = self._client()
        self.mock_token_gen.generate_authorization_code.return_value = "newcode"
        expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        self.mock_code_repo.create.return_value = AuthorizationCode(
            code="newcode", client_id="mcp_x", user_id=42,
            redirect_uri="https://a/cb", code_challenge="ch",
            code_challenge_method="S256", scope="mcp:read",
            expires_at=expires, used=False,
        )

        code = self.use_case.execute(
            client_id="mcp_x", user_id=42, redirect_uri="https://a/cb",
            code_challenge="ch", code_challenge_method="S256", scope="mcp:read",
        )

        self.assertEqual(code.code, "newcode")
        self.mock_client_repo.assign_user.assert_called_once_with("mcp_x", user_id=42)
        self.mock_code_repo.create.assert_called_once()

    def test_unknown_client_raises(self):
        self.mock_client_repo.get_by_client_id.return_value = None
        with self.assertRaises(InvalidClientError):
            self.use_case.execute(
                client_id="mcp_unknown", user_id=42, redirect_uri="https://a/cb",
                code_challenge="ch", code_challenge_method="S256", scope="mcp:read",
            )

    def test_redirect_uri_must_match(self):
        self.mock_client_repo.get_by_client_id.return_value = self._client()
        with self.assertRaises(InvalidRequestError):
            self.use_case.execute(
                client_id="mcp_x", user_id=42, redirect_uri="https://OTHER/cb",
                code_challenge="ch", code_challenge_method="S256", scope="mcp:read",
            )

    def test_requires_s256_challenge_method(self):
        self.mock_client_repo.get_by_client_id.return_value = self._client()
        with self.assertRaises(InvalidRequestError):
            self.use_case.execute(
                client_id="mcp_x", user_id=42, redirect_uri="https://a/cb",
                code_challenge="ch", code_challenge_method="plain", scope="mcp:read",
            )
