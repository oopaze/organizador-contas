from modules.userdata.domains import UserDomain
from modules.userdata.models import User, Profile
from modules.userdata.factories import ProfileFactory


class UserFactory:
    def __init__(self, profile_factory: ProfileFactory):
        self.profile_factory = profile_factory

    def build_from_model(self, model: User) -> UserDomain:
        try:
            profile = self.profile_factory.build_from_model(model.profile)
        except Profile.DoesNotExist:
            profile = None

        return UserDomain(
            id=model.id,
            email=model.email,
            is_active=model.is_active,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
            profile=profile,
        )

