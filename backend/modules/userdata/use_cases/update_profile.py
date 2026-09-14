from decimal import Decimal
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.profile import ProfileSerializer

class UpdateProfileUseCase:
    def __init__(self, profile_repository: "ProfileRepository", profile_serializer: "ProfileSerializer"):
        self.profile_repository = profile_repository
        self.profile_serializer = profile_serializer

    def execute(
        self,
        profile_id: int,
        data: dict = None,
        monthly_spending_goal: Decimal = None,
        monthly_savings_goal: Decimal = None,
        monthly_essentials_goal: Decimal = None,
    ) -> dict:
        profile = self.profile_repository.get(profile_id)
        
        # Build update_data dict
        if data is None:
            data = {}
        else:
            data = data.copy()
        
        if monthly_spending_goal is not None:
            data['monthly_spending_goal'] = monthly_spending_goal
        if monthly_savings_goal is not None:
            data['monthly_savings_goal'] = monthly_savings_goal
        if monthly_essentials_goal is not None:
            data['monthly_essentials_goal'] = monthly_essentials_goal
        
        profile.update(data)
        updated_profile = self.profile_repository.update(profile)
        return self.profile_serializer.serialize(updated_profile)
