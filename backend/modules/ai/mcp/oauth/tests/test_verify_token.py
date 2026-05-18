from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.domains.access_token import AccessToken
from modules.ai.mcp.oauth.use_cases.verify_token import VerifyTokenUseCase


class TestVerifyTokenUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_token_repo = Mock()
        self.mock_token_gen = Mock()
        self.use_case = VerifyTokenUseCase(
            access_token_repository=self.mock_token_repo,
            token_generator=self.mock_token_gen,
        )

    def test_returns_user_id_for_valid_token(self):
        self.mock_token_gen.hash_token.return_value = "h"
        self.mock_token_repo.get_by_hash.return_value = AccessToken(
            token_hash="h", client_id="mcp_x", user_id=42, scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked_at=None,
        )
        self.assertEqual(self.use_case.execute(plaintext_token="some-tok"), 42)

    def test_returns_none_for_unknown_token(self):
        self.mock_token_gen.hash_token.return_value = "h"
        self.mock_token_repo.get_by_hash.return_value = None
        self.assertIsNone(self.use_case.execute(plaintext_token="bad"))

    def test_returns_none_for_revoked_token(self):
        self.mock_token_gen.hash_token.return_value = "h"
        self.mock_token_repo.get_by_hash.return_value = AccessToken(
            token_hash="h", client_id="mcp_x", user_id=42, scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked_at=datetime.now(timezone.utc),
        )
        self.assertIsNone(self.use_case.execute(plaintext_token="t"))

    def test_returns_none_for_expired_token(self):
        self.mock_token_gen.hash_token.return_value = "h"
        self.mock_token_repo.get_by_hash.return_value = AccessToken(
            token_hash="h", client_id="mcp_x", user_id=42, scope="mcp:read",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            revoked_at=None,
        )
        self.assertIsNone(self.use_case.execute(plaintext_token="t"))
