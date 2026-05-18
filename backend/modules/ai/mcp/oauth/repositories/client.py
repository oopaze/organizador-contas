from typing import Optional

from modules.ai.mcp.models import MCPOAuthClient
from modules.ai.mcp.oauth.domains.client import OAuthClient
from modules.ai.mcp.oauth.factories.client import OAuthClientFactory


class OAuthClientRepository:
    def __init__(self, factory: OAuthClientFactory):
        self.factory = factory

    def create(self, *, client_id: str, name: str,
               redirect_uris: list[str]) -> OAuthClient:
        m = MCPOAuthClient.objects.create(
            client_id=client_id, name=name, redirect_uris=redirect_uris,
        )
        return self.factory.from_model(m)

    def get_by_client_id(self, client_id: str) -> Optional[OAuthClient]:
        try:
            m = MCPOAuthClient.objects.get(client_id=client_id, is_active=True)
        except MCPOAuthClient.DoesNotExist:
            return None
        return self.factory.from_model(m)

    def assign_user(self, client_id: str, *, user_id: int) -> None:
        MCPOAuthClient.objects.filter(client_id=client_id, user_id__isnull=True).update(user_id=user_id)

    def list_for_user(self, user_id: int) -> list[OAuthClient]:
        return [
            self.factory.from_model(m)
            for m in MCPOAuthClient.objects.filter(user_id=user_id, is_active=True).order_by("-created_at")
        ]

    def count_for_user(self, user_id: int) -> int:
        return MCPOAuthClient.objects.filter(user_id=user_id, is_active=True).count()
