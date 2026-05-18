import hashlib
import secrets


class TokenGeneratorService:
    """Generates client IDs, authorization codes, and access tokens.

    Access tokens are returned as (plaintext, sha256_hex_hash). Only the hash
    is persisted; plaintext is shown to the client exactly once.
    """

    def generate_client_id(self) -> str:
        return f"mcp_{secrets.token_urlsafe(24)}"

    def generate_authorization_code(self) -> str:
        return secrets.token_urlsafe(32)

    def generate_access_token(self) -> tuple[str, str]:
        plaintext = f"mcp_at_{secrets.token_urlsafe(32)}"
        return plaintext, self.hash_token(plaintext)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
