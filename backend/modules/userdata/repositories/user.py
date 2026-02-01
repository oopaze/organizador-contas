from typing import Optional, TYPE_CHECKING

from modules.userdata.domains.user import UserDomain
from modules.userdata.factories.user import UserFactory

if TYPE_CHECKING:
    from modules.userdata.models import User
    from modules.userdata.repositories.profile import ProfileRepository


class UserRepository:
    def __init__(self, model: "User", user_factory: UserFactory, profile_repository: "ProfileRepository"):
        self.model = model
        self.user_factory = user_factory
        self.profile_repository = profile_repository

    def get_by_id(self, user_id: int) -> Optional[UserDomain]:
        user = self.model.objects.filter(id=user_id).select_related("profile").first()
        if not user:
            return None
        return self.user_factory.build_from_model(user)

    def get_by_email(self, email: str) -> Optional[UserDomain]:
        user = self.model.objects.filter(email=email).select_related("profile").first()
        if not user:
            return None
        return self.user_factory.build_from_model(user)

    def authenticate(self, email: str, password: str) -> Optional[UserDomain]:
        user = self.model.objects.filter(email=email, is_active=True).select_related("profile").first()
        if not user or not user.check_password(password):
            return None
        return self.user_factory.build_from_model(user)

    def create(self, email: str, password: str) -> UserDomain:
        user = self.model.objects.create_user(
            email=email,
            password=password,
        )
        return self.user_factory.build_from_model(user)
    
    def update(self, user: UserDomain) -> UserDomain:
        user_instance = self.model.objects.get(id=user.id)
        user_instance.email = user.email
        user_instance.save()
        return self.user_factory.build_from_model(user_instance)


