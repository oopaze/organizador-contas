import os
import pytest

if os.environ.get("MCP_PG_INTEGRATION") != "1":
    pytest.skip(
        "Set MCP_PG_INTEGRATION=1 to run OAuth view integration tests "
        "(requires Postgres).",
        allow_module_level=True,
    )

import base64
import hashlib
import json
import secrets
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


def pkce_pair():
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


class TestOAuthFlow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x", is_active=True)
        self.redirect_uri = "https://app.example.com/cb"
        self.verifier, self.challenge = pkce_pair()

    def _register(self):
        resp = self.client.post(
            "/oauth/register",
            data=json.dumps({
                "client_name": "Test",
                "redirect_uris": [self.redirect_uri],
            }),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        return resp.json()["client_id"]

    def test_full_flow(self):
        client_id = self._register()
        self.client.force_login(self.user)
        # Authorize (POST allow)
        resp = self.client.post("/oauth/authorize", {
            "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "scope": "mcp:read",
            "state": "xyz",
            "decision": "allow",
        })
        self.assertEqual(resp.status_code, 302)
        qs = parse_qs(urlparse(resp.url).query)
        code = qs["code"][0]
        # Token exchange
        resp = self.client.post("/oauth/token", {
            "grant_type": "authorization_code",
            "code": code, "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.verifier,
        })
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "Bearer")

    def test_pkce_failure(self):
        client_id = self._register()
        self.client.force_login(self.user)
        resp = self.client.post("/oauth/authorize", {
            "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_challenge": self.challenge,
            "code_challenge_method": "S256", "scope": "mcp:read",
            "state": "xyz", "decision": "allow",
        })
        code = parse_qs(urlparse(resp.url).query)["code"][0]
        # Wrong verifier
        resp = self.client.post("/oauth/token", {
            "grant_type": "authorization_code",
            "code": code, "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": "WRONG",
        })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_grant")


class TestConnectionsAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x")
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(client_id="mcp_a", name="A", redirect_uris=[], user_id=self.user.id)
        MCPOAuthClient.objects.create(client_id="mcp_b", name="B", redirect_uris=[], user_id=self.user.id)
        self.client.force_login(self.user)

    def test_list_connections(self):
        resp = self.client.get("/api/v1/mcp/connections/")
        self.assertEqual(resp.status_code, 200)
        names = [c["name"] for c in resp.json()["connections"]]
        self.assertIn("A", names)
        self.assertIn("B", names)

    def test_revoke_connection(self):
        resp = self.client.post("/api/v1/mcp/connections/mcp_a/revoke/")
        self.assertEqual(resp.status_code, 200)
