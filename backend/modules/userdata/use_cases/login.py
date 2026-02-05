from typing import Optional

from modules.userdata.gateways.jwt import JWTGateway
from modules.userdata.repositories.user import UserRepository
from modules.userdata.serializers.user import UserSerializer


class LoginUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_gateway: JWTGateway,
        user_serializer: UserSerializer,
    ):
        self.user_repository = user_repository
        self.jwt_gateway = jwt_gateway
        self.user_serializer = user_serializer

    def execute(self, email: str, password: str) -> Optional[dict]:
        user = self.user_repository.authenticate(email, password)
        if not user:
            return None
        if not user.is_active:
            return None
        
        tokens = self.jwt_gateway.generate_tokens(user.id, user.email)
        return {
            "user": self.user_serializer.serialize(user),
            **tokens,
        }

