import jwt
import time
from typing import Optional
from infra.secrets import SECRET_KEY


class ShareTokenService:
    """
    Service for generating and validating share tokens for actors.
    Uses JWT to encode the actor_id, creating a signed token that can be
    shared publicly without exposing the actual ID.
    """

    ALGORITHM = "HS256"
    TOKEN_TYPE = "actor_share"
    TOKEN_EXPIRATION_DAYS = 7

    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key

    def generate_token(self, actor_id: int) -> str:
        payload = {
            "actor_id": actor_id,
            "type": self.TOKEN_TYPE,
            "iat": int(time.time()),
            "exp": int(time.time()) + (self.TOKEN_EXPIRATION_DAYS * 24 * 60 * 60),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    
    def validate_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
            if payload.get("type") != self.TOKEN_TYPE:
                return None
            return payload.get("actor_id")
        except jwt.InvalidTokenError:
            return None

