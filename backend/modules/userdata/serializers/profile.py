from modules.userdata.domains import ProfileDomain


class ProfileSerializer:
    def serialize(self, profile: "ProfileDomain") -> dict:
        return {
            "id": profile.id,
            "bio": profile.bio,
            "salary": profile.salary,
            "full_name": profile.full_name(),
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "created_at": profile.created_at.strftime("%Y-%m-%d %H:%M:%S") if profile.created_at else None,
            "updated_at": profile.updated_at.strftime("%Y-%m-%d %H:%M:%S") if profile.updated_at else None,
        }
