from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt


class JWTGateway:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expiry_minutes = 15
        self.refresh_token_expiry_days = 7

    def generate_access_token(self, user_id: int, email: str) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expiry_minutes),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: int, email: str) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expiry_days),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_tokens(self, user_id: int, email: str) -> dict:
        return {
            "access_token": self.generate_access_token(user_id, email),
            "refresh_token": self.generate_refresh_token(user_id, email),
        }

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def validate_access_token(self, token: str) -> Optional[dict]:
        payload = self.decode_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None

    def validate_refresh_token(self, token: str) -> Optional[dict]:
        payload = self.decode_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None

