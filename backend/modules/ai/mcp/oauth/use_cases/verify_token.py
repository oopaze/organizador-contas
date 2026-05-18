from datetime import datetime, timezone
from typing import Optional


class VerifyTokenUseCase:
    def __init__(self, access_token_repository, token_generator):
        self.access_token_repository = access_token_repository
        self.token_generator = token_generator

    def execute(self, *, plaintext_token: str) -> Optional[int]:
        token_hash = self.token_generator.hash_token(plaintext_token)
        access_token = self.access_token_repository.get_by_hash(token_hash)
        if access_token is None:
            return None
        if not access_token.is_valid(datetime.now(timezone.utc)):
            return None
        return access_token.user_id
