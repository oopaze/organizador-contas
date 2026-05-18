"""Integration tests for OAuth repositories.

Require a running Postgres + applied migrations. Gated by env var
MCP_PG_INTEGRATION=1. Run inside the Docker container or in any env where
the test DB can be created.
"""
import os

import pytest


if os.environ.get("MCP_PG_INTEGRATION") != "1":
    pytest.skip(
        "Set MCP_PG_INTEGRATION=1 to run repository integration tests "
        "(requires Postgres).",
        allow_module_level=True,
    )


from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase

from modules.ai.mcp.models import MCPOAuthClient
from modules.ai.mcp.oauth.factories.client import OAuthClientFactory
from modules.ai.mcp.oauth.factories.auth_code import AuthorizationCodeFactory
from modules.ai.mcp.oauth.factories.access_token import AccessTokenFactory
from modules.ai.mcp.oauth.repositories.client import OAuthClientRepository
from modules.ai.mcp.oauth.repositories.auth_code import AuthorizationCodeRepository
from modules.ai.mcp.oauth.repositories.access_token import AccessTokenRepository


User = get_user_model()


class TestOAuthClientRepository(TestCase):
    def setUp(self):
        self.repo = OAuthClientRepository(factory=OAuthClientFactory())
        self.user = User.objects.create_user(email="u@u.com", password="x")

    def test_create_and_get(self):
        client = self.repo.create(
            client_id="mcp_x",
            name="Test Client",
            redirect_uris=["https://example.com/cb"],
        )
        self.assertEqual(client.client_id, "mcp_x")
        self.assertIsNone(client.user_id)

        fetched = self.repo.get_by_client_id("mcp_x")
        self.assertEqual(fetched.client_id, "mcp_x")

    def test_get_unknown_returns_none(self):
        self.assertIsNone(self.repo.get_by_client_id("mcp_unknown"))

    def test_assign_user(self):
        client = self.repo.create(client_id="mcp_x", name="C", redirect_uris=[])
        self.repo.assign_user(client.client_id, user_id=self.user.id)
        fetched = self.repo.get_by_client_id("mcp_x")
        self.assertEqual(fetched.user_id, self.user.id)


class TestAuthorizationCodeRepository(TestCase):
    def setUp(self):
        self.code_repo = AuthorizationCodeRepository(factory=AuthorizationCodeFactory())
        self.user = User.objects.create_user(email="u@u.com", password="x")
        self.client = MCPOAuthClient.objects.create(
            client_id="mcp_x", name="C", redirect_uris=["https://example.com/cb"],
        )

    def test_create_and_consume(self):
        expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        code = self.code_repo.create(
            code="abcd",
            client_id="mcp_x",
            user_id=self.user.id,
            redirect_uri="https://example.com/cb",
            code_challenge="ch",
            code_challenge_method="S256",
            scope="mcp:read",
            expires_at=expires,
        )
        self.assertEqual(code.code, "abcd")
        self.assertFalse(code.used)

        consumed = self.code_repo.consume(code="abcd")
        self.assertTrue(consumed.used)

        self.assertIsNone(self.code_repo.consume(code="abcd"))


class TestAccessTokenRepository(TestCase):
    def setUp(self):
        self.token_repo = AccessTokenRepository(factory=AccessTokenFactory())
        self.user = User.objects.create_user(email="u@u.com", password="x")
        MCPOAuthClient.objects.create(client_id="mcp_x", name="C", redirect_uris=[])

    def test_create_and_get_by_hash(self):
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        token = self.token_repo.create(
            token_hash="h" * 64,
            client_id="mcp_x",
            user_id=self.user.id,
            scope="mcp:read",
            expires_at=expires,
        )
        self.assertEqual(token.token_hash, "h" * 64)
        fetched = self.token_repo.get_by_hash("h" * 64)
        self.assertEqual(fetched.user_id, self.user.id)

    def test_revoke(self):
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        self.token_repo.create(
            token_hash="h" * 64, client_id="mcp_x", user_id=self.user.id,
            scope="mcp:read", expires_at=expires,
        )
        self.token_repo.revoke_by_hash("h" * 64)
        fetched = self.token_repo.get_by_hash("h" * 64)
        self.assertIsNotNone(fetched.revoked_at)

    def test_revoke_all_for_client_user(self):
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        self.token_repo.create(
            token_hash="a" * 64, client_id="mcp_x", user_id=self.user.id,
            scope="mcp:read", expires_at=expires,
        )
        self.token_repo.create(
            token_hash="b" * 64, client_id="mcp_x", user_id=self.user.id,
            scope="mcp:read", expires_at=expires,
        )
        n = self.token_repo.revoke_all(client_id="mcp_x", user_id=self.user.id)
        self.assertEqual(n, 2)
        self.assertIsNotNone(self.token_repo.get_by_hash("a" * 64).revoked_at)
        self.assertIsNotNone(self.token_repo.get_by_hash("b" * 64).revoked_at)
