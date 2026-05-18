from typing import Optional

from modules.ai.mcp.oauth.container import OAuthContainer


_oauth_container = OAuthContainer()


def user_id_from_bearer_token(authorization_header: Optional[str]) -> Optional[int]:
    if not authorization_header or not authorization_header.lower().startswith("bearer "):
        return None
    token = authorization_header[7:].strip()
    if not token:
        return None
    use_case = _oauth_container.verify_token_use_case()
    return use_case.execute(plaintext_token=token)
