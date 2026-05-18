from django.test import Client, SimpleTestCase


class TestWellKnownEndpoints(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_oauth_authorization_server(self):
        resp = self.client.get("/.well-known/oauth-authorization-server")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("issuer", body)
        self.assertIn("authorization_endpoint", body)
        self.assertEqual(body["code_challenge_methods_supported"], ["S256"])

    def test_oauth_protected_resource(self):
        resp = self.client.get("/.well-known/oauth-protected-resource")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("resource", body)
        self.assertEqual(body["scopes_supported"], ["mcp:read"])
