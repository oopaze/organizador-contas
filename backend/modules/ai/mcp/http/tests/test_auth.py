import os
import pytest

if os.environ.get("MCP_PG_INTEGRATION") != "1":
    pytest.skip(
        "Set MCP_PG_INTEGRATION=1 to run HTTP auth integration tests "
        "(requires Postgres).",
        allow_module_level=True,
    )

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from modules.ai.mcp.http.auth import user_id_from_bearer_token
from modules.ai.mcp.models import MCPOAuthClient, MCPAccessToken
from modules.ai.mcp.oauth.services.token_generator import TokenGeneratorService


User = get_user_model()


class TestBearerAuth(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="u@u.com", password="x")
        self.client_model = MCPOAuthClient.objects.create(
            client_id="mcp_x", name="X", redirect_uris=[], user_id=self.user.id,
        )
        self.gen = TokenGeneratorService()
        plaintext, token_hash = self.gen.generate_access_token()
        MCPAccessToken.objects.create(
            token_hash=token_hash, client_id="mcp_x", user_id=self.user.id,
            scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.plaintext = plaintext

    def test_valid_token_returns_user_id(self):
        self.assertEqual(
            user_id_from_bearer_token(f"Bearer {self.plaintext}"), self.user.id,
        )

    def test_missing_header(self):
        self.assertIsNone(user_id_from_bearer_token(None))

    def test_non_bearer_scheme(self):
        self.assertIsNone(user_id_from_bearer_token("Basic xxx"))

    def test_unknown_token(self):
        self.assertIsNone(user_id_from_bearer_token("Bearer not-a-real-token"))
