from datetime import datetime, timezone
from typing import Optional

from django.db import transaction

from modules.ai.mcp.models import MCPAuthorizationCode, MCPOAuthClient
from modules.ai.mcp.oauth.domains.auth_code import AuthorizationCode
from modules.ai.mcp.oauth.factories.auth_code import AuthorizationCodeFactory


class AuthorizationCodeRepository:
    def __init__(self, factory: AuthorizationCodeFactory):
        self.factory = factory

    def create(
        self, *, code: str, client_id: str, user_id: int, redirect_uri: str,
        code_challenge: str, code_challenge_method: str, scope: str,
        expires_at: datetime,
    ) -> AuthorizationCode:
        client = MCPOAuthClient.objects.get(client_id=client_id)
        m = MCPAuthorizationCode.objects.create(
            code=code, client=client, user_id=user_id,
            redirect_uri=redirect_uri, code_challenge=code_challenge,
            code_challenge_method=code_challenge_method, scope=scope,
            expires_at=expires_at,
        )
        return self.factory.from_model(m)

    @transaction.atomic
    def consume(self, *, code: str) -> Optional[AuthorizationCode]:
        try:
            m = MCPAuthorizationCode.objects.select_for_update().get(code=code, used_at__isnull=True)
        except MCPAuthorizationCode.DoesNotExist:
            return None
        m.used_at = datetime.now(timezone.utc)
        m.save(update_fields=["used_at"])
        return self.factory.from_model(m)
