from datetime import datetime, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.factories.client import OAuthClientFactory
from modules.ai.mcp.oauth.factories.auth_code import AuthorizationCodeFactory
from modules.ai.mcp.oauth.factories.access_token import AccessTokenFactory


class TestOAuthClientFactory(SimpleTestCase):
    def test_from_model_basic(self):
        model = Mock()
        model.client_id = "mcp_abc"
        model.name = "ChatGPT"
        model.redirect_uris = ["https://example.com/cb"]
        model.user_id = 7
        model.is_active = True

        domain = OAuthClientFactory().from_model(model)
        self.assertEqual(domain.client_id, "mcp_abc")
        self.assertEqual(domain.user_id, 7)
        self.assertEqual(domain.redirect_uris, ["https://example.com/cb"])

    def test_from_model_unassigned_user(self):
        model = Mock()
        model.client_id = "mcp_abc"
        model.name = "ChatGPT"
        model.redirect_uris = []
        model.user_id = None
        model.is_active = True
        domain = OAuthClientFactory().from_model(model)
        self.assertIsNone(domain.user_id)


class TestAuthorizationCodeFactory(SimpleTestCase):
    def test_from_model(self):
        model = Mock()
        model.code = "abc"
        model.client = Mock()
        model.client.client_id = "mcp_x"
        model.user_id = 7
        model.redirect_uri = "https://example.com/cb"
        model.code_challenge = "ch"
        model.code_challenge_method = "S256"
        model.scope = "mcp:read"
        model.expires_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        model.used_at = None
        domain = AuthorizationCodeFactory().from_model(model)
        self.assertEqual(domain.code, "abc")
        self.assertFalse(domain.used)


class TestAccessTokenFactory(SimpleTestCase):
    def test_from_model(self):
        model = Mock()
        model.token_hash = "h"
        model.client = Mock()
        model.client.client_id = "mcp_x"
        model.user_id = 7
        model.scope = "mcp:read"
        model.expires_at = datetime(2030, 1, 1, tzinfo=timezone.utc)
        model.revoked_at = None
        domain = AccessTokenFactory().from_model(model)
        self.assertEqual(domain.user_id, 7)
        self.assertIsNone(domain.revoked_at)
