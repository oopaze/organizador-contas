from typing import Optional

from modules.userdata.gateways.jwt import JWTGateway
from modules.userdata.repositories.user import UserRepository
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.user import UserSerializer


class RegisterUseCase:
    def __init__(
        self,
        jwt_gateway: JWTGateway,
        user_repository: UserRepository,
        profile_repository: ProfileRepository,
        user_serializer: UserSerializer,
    ):
        self.jwt_gateway = jwt_gateway
        self.user_repository = user_repository
        self.user_serializer = user_serializer
        self.profile_repository = profile_repository

    def execute(
        self,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> Optional[dict]:
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            return None

        user = self.user_repository.create(email, password)
        self.profile_repository.create(user, first_name, last_name)
        user = self.user_repository.get_by_id(user.id)

        tokens = self.jwt_gateway.generate_tokens(user.id, user.email)
        return {
            "user": self.user_serializer.serialize(user),
            **tokens,
        }

