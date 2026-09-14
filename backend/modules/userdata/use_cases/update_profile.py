from decimal import Decimal, InvalidOperation
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.profile import ProfileSerializer

GOAL_FIELDS = ("spending_goal_percent", "savings_goal_percent", "essentials_goal_percent")


class UpdateProfileUseCase:
    def __init__(self, profile_repository: "ProfileRepository", profile_serializer: "ProfileSerializer"):
        self.profile_repository = profile_repository
        self.profile_serializer = profile_serializer

    def execute(
        self,
        profile_id: int,
        data: dict = None,
        spending_goal_percent: Decimal = None,
        savings_goal_percent: Decimal = None,
        essentials_goal_percent: Decimal = None,
    ) -> dict:
        profile = self.profile_repository.get(profile_id)
        
        # Build update_data dict
        if data is None:
            data = {}
        else:
            data = data.copy()
        
        if spending_goal_percent is not None:
            data['spending_goal_percent'] = spending_goal_percent
        if savings_goal_percent is not None:
            data['savings_goal_percent'] = savings_goal_percent
        if essentials_goal_percent is not None:
            data['essentials_goal_percent'] = essentials_goal_percent

        self._validate_goals(data)

        profile.update(data)
        updated_profile = self.profile_repository.update(profile)
        return self.profile_serializer.serialize(updated_profile)

    def _validate_goals(self, data: dict) -> None:
        for field in GOAL_FIELDS:
            value = data.get(field)
            if value is None:
                continue
            try:
                percent = Decimal(str(value))
            except (InvalidOperation, TypeError, ValueError):
                raise ValueError(f"{field} deve ser um percentual entre 0 e 100")
            if percent < 0 or percent > 100:
                raise ValueError(f"{field} deve estar entre 0 e 100")
