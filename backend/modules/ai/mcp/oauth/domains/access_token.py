from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AccessToken:
    token_hash: str
    client_id: str
    user_id: int
    scope: str
    expires_at: datetime
    revoked_at: Optional[datetime]

    def is_valid(self, now: datetime) -> bool:
        return self.revoked_at is None and now < self.expires_at
