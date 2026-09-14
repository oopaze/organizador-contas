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
                "monthly_spending_goal": Decimal("3000.00"),
                "monthly_savings_goal": Decimal("1000.00"),
                "monthly_essentials_goal": Decimal("1500.00"),
            },
        )

        self.assertEqual(result["monthly_spending_goal"], Decimal("3000.00"))
        self.assertEqual(result["monthly_savings_goal"], Decimal("1000.00"))
        self.assertEqual(result["monthly_essentials_goal"], Decimal("1500.00"))

        domain = self.repository.get_by_user_id(self.user.id)
        self.assertEqual(domain.monthly_spending_goal, Decimal("3000.00"))
        self.assertEqual(domain.monthly_savings_goal, Decimal("1000.00"))
        self.assertEqual(domain.monthly_essentials_goal, Decimal("1500.00"))
