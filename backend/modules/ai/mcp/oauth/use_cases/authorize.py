from datetime import datetime, timedelta, timezone

from modules.ai.mcp.oauth.exceptions import InvalidClientError, InvalidRequestError


AUTH_CODE_TTL = timedelta(minutes=10)


class AuthorizeUseCase:
    def __init__(self, client_repository, auth_code_repository, token_generator):
        self.client_repository = client_repository
        self.auth_code_repository = auth_code_repository
        self.token_generator = token_generator

    def execute(
        self, *, client_id: str, user_id: int, redirect_uri: str,
        code_challenge: str, code_challenge_method: str, scope: str,
    ):
        client = self.client_repository.get_by_client_id(client_id)
        if client is None:
            raise InvalidClientError(f"client {client_id!r} not found")
        if not client.matches_redirect_uri(redirect_uri):
            raise InvalidRequestError("redirect_uri does not match any registered URI")
        if code_challenge_method != "S256":
            raise InvalidRequestError("only S256 code_challenge_method is supported")
        if not code_challenge:
            raise InvalidRequestError("code_challenge is required")
        if scope != "mcp:read":
            raise InvalidRequestError(f"unsupported scope: {scope!r}")

        if client.user_id is None:
            self.client_repository.assign_user(client_id, user_id=user_id)
        elif client.user_id != user_id:
            raise InvalidClientError("client owned by another user")

        code = self.token_generator.generate_authorization_code()
        expires_at = datetime.now(timezone.utc) + AUTH_CODE_TTL
        return self.auth_code_repository.create(
            code=code, client_id=client_id, user_id=user_id,
            redirect_uri=redirect_uri, code_challenge=code_challenge,
            code_challenge_method=code_challenge_method, scope=scope,
            expires_at=expires_at,
        )
