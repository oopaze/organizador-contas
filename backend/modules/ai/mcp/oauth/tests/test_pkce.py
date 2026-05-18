import base64
import hashlib

from django.test import SimpleTestCase

from modules.ai.mcp.oauth.services.pkce import PKCEService


class TestPKCEService(SimpleTestCase):
    def setUp(self):
        self.service = PKCEService()

    def _challenge(self, verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    def test_verify_valid_s256(self):
        verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        challenge = self._challenge(verifier)
        self.assertTrue(self.service.verify(verifier, challenge, method="S256"))

    def test_verify_mismatched(self):
        challenge = self._challenge("verifier-A")
        self.assertFalse(self.service.verify("verifier-B", challenge, method="S256"))

    def test_rejects_plain_method(self):
        self.assertFalse(self.service.verify("v", "v", method="plain"))

    def test_rejects_unknown_method(self):
        self.assertFalse(self.service.verify("v", "c", method="md5"))
