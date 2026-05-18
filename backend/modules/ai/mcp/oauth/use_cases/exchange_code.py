from datetime import datetime, timedelta, timezone

from modules.ai.mcp.oauth.exceptions import InvalidGrantError


ACCESS_TOKEN_TTL = timedelta(days=7)


class ExchangeCodeUseCase:
    def __init__(
        self, auth_code_repository, access_token_repository,
        token_generator, pkce_service,
    ):
        self.auth_code_repository = auth_code_repository
        self.access_token_repository = access_token_repository
        self.token_generator = token_generator
        self.pkce_service = pkce_service

    def execute(self, *, code: str, client_id: str, redirect_uri: str,
                code_verifier: str) -> dict:
        auth_code = self.auth_code_repository.consume(code=code)
        if auth_code is None:
            raise InvalidGrantError("invalid or already-used code")
        now = datetime.now(timezone.utc)
        if auth_code.is_expired(now):
            raise InvalidGrantError("code expired")
        if auth_code.client_id != client_id:
            raise InvalidGrantError("client_id mismatch")
        if auth_code.redirect_uri != redirect_uri:
            raise InvalidGrantError("redirect_uri mismatch")
        if not self.pkce_service.verify(
            code_verifier, auth_code.code_challenge,
            method=auth_code.code_challenge_method,
        ):
            raise InvalidGrantError("PKCE verification failed")

        plaintext, token_hash = self.token_generator.generate_access_token()
        expires_at = now + ACCESS_TOKEN_TTL
        self.access_token_repository.create(
            token_hash=token_hash, client_id=auth_code.client_id,
            user_id=auth_code.user_id, scope=auth_code.scope,
            expires_at=expires_at,
        )
        return {
            "access_token": plaintext,
            "token_type": "Bearer",
            "expires_in": int(ACCESS_TOKEN_TTL.total_seconds()),
            "scope": auth_code.scope,
        }
