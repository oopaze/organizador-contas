from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.profile import ProfileSerializer

class UpdateProfileUseCase:
    def __init__(self, profile_repository: "ProfileRepository", profile_serializer: "ProfileSerializer"):
        self.profile_repository = profile_repository
        self.profile_serializer = profile_serializer

    def execute(self, profile_id: int, data: dict) -> dict:
        profile = self.profile_repository.get(profile_id)
        profile.update(data)
        updated_profile = self.profile_repository.update(profile)
        return self.profile_serializer.serialize(updated_profile)
