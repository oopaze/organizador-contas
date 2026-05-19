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
        from modules.userdata.gateways.jwt import JWTGateway
        from django.conf import settings as dj_settings
        token = JWTGateway(secret_key=dj_settings.SECRET_KEY).generate_access_token(user_id=self.user.id, email=self.user.email)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": client_id,
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "xyz",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(resp.json()["redirect_to"]).query)
        code = qs["code"][0]
        # Token exchange — unchanged
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
        from modules.userdata.gateways.jwt import JWTGateway
        from django.conf import settings as dj_settings
        token = JWTGateway(secret_key=dj_settings.SECRET_KEY).generate_access_token(user_id=self.user.id, email=self.user.email)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": client_id,
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "xyz",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        from urllib.parse import urlparse, parse_qs
        code = parse_qs(urlparse(resp.json()["redirect_to"]).query)["code"][0]
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


class TestAuthorizeRedirect(TestCase):
    def setUp(self):
        self.client = Client()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_abc", name="Claude",
            redirect_uris=["https://app.example.com/cb"],
        )

    def test_get_redirects_to_spa_with_query_string(self):
        from django.test import override_settings
        with override_settings(MCP_OAUTH_FRONTEND_URL="https://app.poupix.test"):
            resp = self.client.get(
                "/oauth/authorize",
                {
                    "client_id": "mcp_abc",
                    "redirect_uri": "https://app.example.com/cb",
                    "code_challenge": "abc",
                    "code_challenge_method": "S256",
                    "scope": "mcp:read",
                    "state": "xyz",
                },
            )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith("https://app.poupix.test/oauth/authorize?"),
            resp.url,
        )
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(resp.url).query)
        self.assertEqual(qs["client_id"], ["mcp_abc"])
        self.assertEqual(qs["state"], ["xyz"])
        self.assertEqual(qs["code_challenge"], ["abc"])


class TestClientInfoEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_known",
            name="Claude",
            redirect_uris=["https://claude.ai/cb"],
        )

    def test_returns_client_info_without_auth(self):
        resp = self.client.get("/api/v1/mcp/oauth/client/mcp_known/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["client_id"], "mcp_known")
        self.assertEqual(body["name"], "Claude")
        self.assertEqual(body["redirect_uris"], ["https://claude.ai/cb"])

    def test_unknown_client_returns_404(self):
        resp = self.client.get("/api/v1/mcp/oauth/client/missing/")
        self.assertEqual(resp.status_code, 404)


class TestAuthorizeApiEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x", is_active=True)
        self.redirect_uri = "https://app.example.com/cb"
        self.verifier, self.challenge = pkce_pair()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_x", name="Claude",
            redirect_uris=[self.redirect_uri],
        )

    def _jwt_for(self, user):
        from django.conf import settings as dj_settings
        from modules.userdata.gateways.jwt import JWTGateway
        return JWTGateway(secret_key=dj_settings.SECRET_KEY).generate_access_token(
            user_id=user.id, email=user.email
        )

    def test_happy_path_returns_redirect_to_with_code_and_state(self):
        token = self._jwt_for(self.user)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": "mcp_x",
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "st-1",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertIn("redirect_to", body)
        self.assertTrue(body["redirect_to"].startswith(self.redirect_uri + "?"))
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(body["redirect_to"]).query)
        self.assertIn("code", qs)
        self.assertEqual(qs["state"], ["st-1"])

    def test_requires_jwt(self):
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({"client_id": "mcp_x"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_mismatched_redirect_uri_returns_400(self):
        token = self._jwt_for(self.user)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": "mcp_x",
                "redirect_uri": "https://evil.example.com/cb",
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "st",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_request")
