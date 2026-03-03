import jwt
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
    
    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key
    
    def generate_token(self, actor_id: int) -> str:
        """Generate a share token for an actor."""
        payload = {
            "actor_id": actor_id,
            "type": self.TOKEN_TYPE,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    
    def validate_token(self, token: str) -> Optional[int]:
        """
        Validate a share token and return the actor_id.
        Returns None if the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
            if payload.get("type") != self.TOKEN_TYPE:
                return None
            return payload.get("actor_id")
        except jwt.InvalidTokenError:
            return None

