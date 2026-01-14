from modules.userdata.domains.user import UserDomain
from modules.userdata.serializers.profile import ProfileSerializer


class UserSerializer:
    def __init__(self, profile_serializer: "ProfileSerializer"):
        self.profile_serializer = profile_serializer

    def serialize(self, user: UserDomain) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
            "updated_at": user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else None,
            "profile": self.profile_serializer.serialize(user.profile) if user.profile else None,
        }

