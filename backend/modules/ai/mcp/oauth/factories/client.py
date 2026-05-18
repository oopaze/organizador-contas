from modules.ai.mcp.oauth.domains.client import OAuthClient


class OAuthClientFactory:
    def from_model(self, model) -> OAuthClient:
        return OAuthClient(
            client_id=model.client_id,
            name=model.name,
            redirect_uris=list(model.redirect_uris or []),
            user_id=model.user_id,
            is_active=model.is_active,
        )
