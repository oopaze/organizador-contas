import base64
import hashlib
import hmac


class PKCEService:
    """Verifies PKCE code_verifier against code_challenge (S256 only)."""

    def verify(self, verifier: str, challenge: str, *, method: str) -> bool:
        if method != "S256":
            return False
        if not verifier or not challenge:
            return False
        digest = hashlib.sha256(verifier.encode()).digest()
        expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return hmac.compare_digest(expected, challenge)
