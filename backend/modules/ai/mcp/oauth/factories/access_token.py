from modules.ai.mcp.oauth.domains.access_token import AccessToken


class AccessTokenFactory:
    def from_model(self, model) -> AccessToken:
        return AccessToken(
            token_hash=model.token_hash,
            client_id=model.client.client_id,
            user_id=model.user_id,
            scope=model.scope,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )
