from typing import Optional

from modules.userdata.repositories.user import UserRepository
from modules.userdata.serializers.user import UserSerializer


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository, user_serializer: UserSerializer):
        self.user_repository = user_repository
        self.user_serializer = user_serializer

    def execute(self, user_id: int) -> Optional[dict]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return self.user_serializer.serialize(user)

