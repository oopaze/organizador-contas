from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.use_cases.revoke import RevokeUseCase


class TestRevokeUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_token_repo = Mock()
        self.mock_token_gen = Mock()
        self.use_case = RevokeUseCase(
            access_token_repository=self.mock_token_repo,
            token_generator=self.mock_token_gen,
        )

    def test_revoke_by_plaintext_token(self):
        self.mock_token_gen.hash_token.return_value = "h"
        self.mock_token_repo.revoke_by_hash.return_value = 1
        self.assertEqual(self.use_case.execute_by_token(plaintext_token="t"), 1)
        self.mock_token_repo.revoke_by_hash.assert_called_once_with("h")

    def test_revoke_all_for_client_and_user(self):
        self.mock_token_repo.revoke_all.return_value = 3
        self.assertEqual(
            self.use_case.execute_by_client(client_id="mcp_x", user_id=42), 3
        )
        self.mock_token_repo.revoke_all.assert_called_once_with(
            client_id="mcp_x", user_id=42,
        )
