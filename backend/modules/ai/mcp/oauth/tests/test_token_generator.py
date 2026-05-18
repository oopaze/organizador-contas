import re

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.services.token_generator import TokenGeneratorService


class TestTokenGeneratorService(SimpleTestCase):
    def setUp(self):
        self.service = TokenGeneratorService()

    def test_generate_client_id(self):
        cid = self.service.generate_client_id()
        self.assertTrue(cid.startswith("mcp_"))
        self.assertGreater(len(cid), 16)

    def test_generate_authorization_code(self):
        code = self.service.generate_authorization_code()
        self.assertGreaterEqual(len(code), 32)
        self.assertTrue(re.fullmatch(r"[A-Za-z0-9_-]+", code))

    def test_generate_access_token(self):
        plaintext, token_hash = self.service.generate_access_token()
        self.assertTrue(plaintext.startswith("mcp_at_"))
        self.assertEqual(len(token_hash), 64)
        self.assertEqual(self.service.hash_token(plaintext), token_hash)

    def test_hash_token_is_sha256_hex(self):
        h = self.service.hash_token("some-token")
        self.assertEqual(len(h), 64)
        self.assertTrue(re.fullmatch(r"[a-f0-9]+", h))
