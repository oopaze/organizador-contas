from typing import Optional

from modules.userdata.gateways.jwt import JWTGateway
from modules.userdata.repositories.user import UserRepository


class RefreshTokenUseCase:
    def __init__(self, user_repository: UserRepository, jwt_gateway: JWTGateway):
        self.user_repository = user_repository
        self.jwt_gateway = jwt_gateway

    def execute(self, refresh_token: str) -> Optional[dict]:
        payload = self.jwt_gateway.validate_refresh_token(refresh_token)
        if not payload:
            return None

        user = self.user_repository.get_by_id(payload["user_id"])
        if not user:
            return None

        return self.jwt_gateway.generate_tokens(user.id, user.email)

