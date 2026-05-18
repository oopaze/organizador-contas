from modules.ai.mcp.oauth.domains.auth_code import AuthorizationCode


class AuthorizationCodeFactory:
    def from_model(self, model) -> AuthorizationCode:
        return AuthorizationCode(
            code=model.code,
            client_id=model.client.client_id,
            user_id=model.user_id,
            redirect_uri=model.redirect_uri,
            code_challenge=model.code_challenge,
            code_challenge_method=model.code_challenge_method,
            scope=model.scope,
            expires_at=model.expires_at,
            used=model.used_at is not None,
        )
