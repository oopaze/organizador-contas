from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.domains.auth_code import AuthorizationCode
from modules.ai.mcp.oauth.domains.access_token import AccessToken
from modules.ai.mcp.oauth.exceptions import InvalidGrantError
from modules.ai.mcp.oauth.use_cases.exchange_code import ExchangeCodeUseCase


class TestExchangeCodeUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_code_repo = Mock()
        self.mock_token_repo = Mock()
        self.mock_token_gen = Mock()
        self.mock_pkce = Mock()
        self.use_case = ExchangeCodeUseCase(
            auth_code_repository=self.mock_code_repo,
            access_token_repository=self.mock_token_repo,
            token_generator=self.mock_token_gen,
            pkce_service=self.mock_pkce,
        )

    def _auth_code(self, used=False, expired=False):
        future = datetime.now(timezone.utc) + timedelta(minutes=5)
        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        return AuthorizationCode(
            code="abcd", client_id="mcp_x", user_id=42,
            redirect_uri="https://a/cb", code_challenge="ch",
            code_challenge_method="S256", scope="mcp:read",
            expires_at=(past if expired else future), used=used,
        )

    def test_exchanges_valid_code(self):
        self.mock_code_repo.consume.return_value = self._auth_code()
        self.mock_pkce.verify.return_value = True
        self.mock_token_gen.generate_access_token.return_value = ("mcp_at_plain", "hash" * 16)
        self.mock_token_repo.create.return_value = AccessToken(
            token_hash="hash" * 16, client_id="mcp_x", user_id=42,
            scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            revoked_at=None,
        )
        result = self.use_case.execute(
            code="abcd", client_id="mcp_x", redirect_uri="https://a/cb",
            code_verifier="v",
        )
        self.assertEqual(result["access_token"], "mcp_at_plain")
        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(result["expires_in"], 7 * 24 * 3600)
        self.assertEqual(result["scope"], "mcp:read")

    def test_unknown_code_raises(self):
        self.mock_code_repo.consume.return_value = None
        with self.assertRaises(InvalidGrantError):
            self.use_case.execute(
                code="abcd", client_id="mcp_x", redirect_uri="https://a/cb",
                code_verifier="v",
            )

    def test_expired_code_raises(self):
        self.mock_code_repo.consume.return_value = self._auth_code(expired=True)
        with self.assertRaises(InvalidGrantError):
            self.use_case.execute(
                code="abcd", client_id="mcp_x", redirect_uri="https://a/cb",
                code_verifier="v",
            )

    def test_client_id_mismatch_raises(self):
        self.mock_code_repo.consume.return_value = self._auth_code()
        with self.assertRaises(InvalidGrantError):
            self.use_case.execute(
                code="abcd", client_id="mcp_OTHER", redirect_uri="https://a/cb",
                code_verifier="v",
            )

    def test_redirect_uri_mismatch_raises(self):
        self.mock_code_repo.consume.return_value = self._auth_code()
        with self.assertRaises(InvalidGrantError):
            self.use_case.execute(
                code="abcd", client_id="mcp_x", redirect_uri="https://OTHER/cb",
                code_verifier="v",
            )

    def test_pkce_failure_raises(self):
        self.mock_code_repo.consume.return_value = self._auth_code()
        self.mock_pkce.verify.return_value = False
        with self.assertRaises(InvalidGrantError):
            self.use_case.execute(
                code="abcd", client_id="mcp_x", redirect_uri="https://a/cb",
                code_verifier="wrong",
            )
