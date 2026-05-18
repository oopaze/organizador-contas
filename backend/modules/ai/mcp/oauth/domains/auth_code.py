from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuthorizationCode:
    code: str
    client_id: str
    user_id: int
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str
    scope: str
    expires_at: datetime
    used: bool

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at
