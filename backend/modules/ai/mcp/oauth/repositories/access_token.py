from datetime import datetime, timezone
from typing import Optional

from modules.ai.mcp.models import MCPAccessToken
from modules.ai.mcp.oauth.domains.access_token import AccessToken
from modules.ai.mcp.oauth.factories.access_token import AccessTokenFactory


class AccessTokenRepository:
    def __init__(self, factory: AccessTokenFactory):
        self.factory = factory

    def create(self, *, token_hash: str, client_id: str, user_id: int,
               scope: str, expires_at: datetime) -> AccessToken:
        m = MCPAccessToken.objects.create(
            token_hash=token_hash, client_id=client_id, user_id=user_id,
            scope=scope, expires_at=expires_at,
        )
        return self.factory.from_model(m)

    def get_by_hash(self, token_hash: str) -> Optional[AccessToken]:
        try:
            m = MCPAccessToken.objects.get(token_hash=token_hash)
        except MCPAccessToken.DoesNotExist:
            return None
        return self.factory.from_model(m)

    def revoke_by_hash(self, token_hash: str) -> int:
        return MCPAccessToken.objects.filter(
            token_hash=token_hash, revoked_at__isnull=True
        ).update(revoked_at=datetime.now(timezone.utc))

    def revoke_all(self, *, client_id: str, user_id: int) -> int:
        return MCPAccessToken.objects.filter(
            client_id=client_id, user_id=user_id, revoked_at__isnull=True
        ).update(revoked_at=datetime.now(timezone.utc))
