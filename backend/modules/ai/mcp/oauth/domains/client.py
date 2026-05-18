from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class OAuthClient:
    client_id: str
    name: str
    redirect_uris: list[str]
    user_id: Optional[int]
    is_active: bool = True

    def matches_redirect_uri(self, uri: str) -> bool:
        return uri in self.redirect_uris
