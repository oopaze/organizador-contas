from decimal import Decimal

from django.test import TransactionTestCase

from modules.userdata.factories.profile import ProfileFactory
from modules.userdata.models import Profile, User
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.profile import ProfileSerializer
from modules.userdata.use_cases.update_profile import UpdateProfileUseCase


class TestProfileGoalsPersistence(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="goals@test.com", password="pass")
        self.profile = Profile.objects.create(user=self.user)
        self.repository = ProfileRepository(model=Profile, profile_factory=ProfileFactory())
        self.use_case = UpdateProfileUseCase(
            profile_repository=self.repository,
            profile_serializer=ProfileSerializer(),
        )

    def test_update_profile_persists_goals_and_factory_roundtrip(self):
        result = self.use_case.execute(
            self.profile.id,
            data={
                "spending_goal_percent": Decimal("60.00"),
                "savings_goal_percent": Decimal("20.00"),
                "essentials_goal_percent": Decimal("30.00"),
            },
        )

        self.assertEqual(result["spending_goal_percent"], Decimal("60.00"))
        self.assertEqual(result["savings_goal_percent"], Decimal("20.00"))
        self.assertEqual(result["essentials_goal_percent"], Decimal("30.00"))

        domain = self.repository.get_by_user_id(self.user.id)
        self.assertEqual(domain.spending_goal_percent, Decimal("60.00"))
        self.assertEqual(domain.savings_goal_percent, Decimal("20.00"))
        self.assertEqual(domain.essentials_goal_percent, Decimal("30.00"))
