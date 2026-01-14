from modules.userdata.domains import ProfileDomain
from modules.userdata.models import Profile


class ProfileFactory:
    def build_from_model(self, model: "Profile") -> "ProfileDomain":
        return ProfileDomain(
            bio=model.bio,
            salary=model.salary,
            first_name=model.first_name,
            last_name=model.last_name,
            user_id=model.user.id,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
