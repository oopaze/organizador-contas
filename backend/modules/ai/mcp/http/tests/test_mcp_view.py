import os
import pytest

if os.environ.get("MCP_PG_INTEGRATION") != "1":
    pytest.skip(
        "Set MCP_PG_INTEGRATION=1 to run MCP view integration tests "
        "(requires Postgres).",
        allow_module_level=True,
    )

import json
from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from modules.ai.mcp.models import MCPOAuthClient, MCPAccessToken
from modules.ai.mcp.oauth.services.token_generator import TokenGeneratorService


User = get_user_model()


class TestMCPView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x")
        MCPOAuthClient.objects.create(
            client_id="mcp_x", name="X", redirect_uris=[], user_id=self.user.id,
        )
        gen = TokenGeneratorService()
        plaintext, h = gen.generate_access_token()
        MCPAccessToken.objects.create(
            token_hash=h, client_id="mcp_x", user_id=self.user.id,
            scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.token = plaintext

    def _post(self, body, token=None):
        return self.client.post(
            "/mcp",
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token or self.token}",
        )

    def test_unauthorized_without_token(self):
        resp = self.client.post(
            "/mcp", data="{}", content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_initialize(self):
        resp = self._post({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["result"]["serverInfo"]["name"], "poupix-mcp")

    def test_tools_list(self):
        resp = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        names = sorted(t["name"] for t in body["result"]["tools"])
        self.assertEqual(names, ["describe_schema", "execute_sql", "list_enums"])

    def test_invalid_token(self):
        resp = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"}, token="bad-token")
        self.assertEqual(resp.status_code, 401)
