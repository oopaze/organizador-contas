from modules.userdata.domains import ProfileDomain


class ProfileSerializer:
    class Meta:
        fields = (
            'id',
            'bio',
            'salary',
            'salary_day',
            'full_name',
            'first_name',
            'last_name',
            'modo_on',
            'created_at',
            'updated_at',
            'spending_goal_percent',
            'savings_goal_percent',
            'essentials_goal_percent',
        )

    def serialize(self, profile: "ProfileDomain") -> dict:
        return {
            "id": profile.id,
            "bio": profile.bio,
            "salary": profile.salary,
            "salary_day": profile.salary_day,
            "full_name": profile.full_name(),
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "modo_on": profile.modo_on,
            "created_at": profile.created_at.strftime("%Y-%m-%d %H:%M:%S") if profile.created_at else None,
            "updated_at": profile.updated_at.strftime("%Y-%m-%d %H:%M:%S") if profile.updated_at else None,
            "spending_goal_percent": getattr(profile, 'spending_goal_percent', None),
            "savings_goal_percent": getattr(profile, 'savings_goal_percent', None),
            "essentials_goal_percent": getattr(profile, 'essentials_goal_percent', None),
        }
