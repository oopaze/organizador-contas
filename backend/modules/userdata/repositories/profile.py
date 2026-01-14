from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.userdata.models import Profile
    from modules.userdata.factories import ProfileFactory
    from modules.userdata.domains import ProfileDomain
    from modules.userdata.domains import UserDomain

class ProfileRepository:
    def __init__(self, model: "Profile", profile_factory: "ProfileFactory"):
        self.model = model
        self.profile_factory = profile_factory

    def get(self, profile_id: int) -> "ProfileDomain":
        profile_instance = self.model.objects.get(id=profile_id)
        return self.profile_factory.build_from_model(profile_instance)
    
    def get_by_user(self, user: "UserDomain") -> "ProfileDomain":
        profile_instance = self.model.objects.get(user=user.id)
        return self.profile_factory.build_from_model(profile_instance)
    
    def create(self, user: "UserDomain", first_name: str = "", last_name: str = "", bio: str = "", salary: float = 0.0) -> "ProfileDomain":
        profile_instance = self.model.objects.create(user_id=user.id, first_name=first_name, last_name=last_name, bio=bio, salary=salary)
        return self.profile_factory.build_from_model(profile_instance)
    
    def update(self, profile: "ProfileDomain") -> "ProfileDomain":
        profile_instance = self.model.objects.get(id=profile.id)
        profile_instance.first_name = profile.first_name
        profile_instance.last_name = profile.last_name
        profile_instance.bio = profile.bio
        profile_instance.salary = profile.salary
        profile_instance.save()
        return self.profile_factory.build_from_model(profile_instance)
    
    def delete(self, profile_id: int):
        self.model.objects.get(id=profile_id).delete()
