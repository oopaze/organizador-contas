from decimal import Decimal
from unittest.mock import Mock

from django.test import TransactionTestCase

from modules.planning.factories.intention import PurchaseIntentionFactory
from modules.planning.models import PurchaseIntention
from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.use_cases.intention.projection import ProjectionUseCase
from modules.userdata.factories.profile import ProfileFactory
from modules.userdata.models import Profile, User
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.profile import ProfileSerializer
from modules.userdata.use_cases.update_profile import UpdateProfileUseCase


class TestGoalsFullFlow(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="flow@test.com", password="pass")
        self.profile = Profile.objects.create(user=self.user)

        self.profile_repository = ProfileRepository(model=Profile, profile_factory=ProfileFactory())
        self.update_use_case = UpdateProfileUseCase(
            profile_repository=self.profile_repository,
            profile_serializer=ProfileSerializer(),
        )

        self.intention_repository = PurchaseIntentionRepository(
            model=PurchaseIntention,
            intention_factory=PurchaseIntentionFactory(),
        )
        self.sub_transaction_repository = Mock()
        self.sub_transaction_repository.get_by_date_range.return_value = []
        self.projection_use_case = ProjectionUseCase(
            self.intention_repository,
            self.profile_repository,
            self.sub_transaction_repository,
        )

    def test_goals_flow_update_to_projection(self):
        self.update_use_case.execute(
            self.profile.id,
            data={
                "monthly_spending_goal": Decimal("3000.00"),
                "monthly_savings_goal": Decimal("1000.00"),
                "monthly_essentials_goal": Decimal("1500.00"),
            },
        )

        result = self.projection_use_case.execute(self.user.id, months=3)

        self.assertEqual(result["goals"]["monthly_spending_goal"], "3000.00")
        self.assertEqual(result["goals"]["monthly_savings_goal"], "1000.00")
        self.assertEqual(result["goals"]["monthly_essentials_goal"], "1500.00")
        self.assertEqual(len(result["months"]), 3)

    def test_projection_goals_null_when_not_set(self):
        result = self.projection_use_case.execute(self.user.id, months=2)

        self.assertIsNone(result["goals"]["monthly_spending_goal"])
        self.assertIsNone(result["goals"]["monthly_savings_goal"])
        self.assertIsNone(result["goals"]["monthly_essentials_goal"])


class TestProjectionRangeIntegration(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="range@test.com", password="pass")
        Profile.objects.create(user=self.user)
        self.intention_repository = PurchaseIntentionRepository(
            model=PurchaseIntention,
            intention_factory=PurchaseIntentionFactory(),
        )
        self.profile_repository = ProfileRepository(
            model=Profile, profile_factory=ProfileFactory()
        )
        self.sub_transaction_repository = Mock()
        self.sub_transaction_repository.get_by_date_range.return_value = []
        self.use_case = ProjectionUseCase(
            self.intention_repository,
            self.profile_repository,
            self.sub_transaction_repository,
        )

    def _create_intention(self, name: str, amount: str, month: str, installments: int):
        PurchaseIntention.objects.create(
            user_id=self.user.id,
            name=name,
            amount=amount,
            month=month,
            installments=installments,
            status="planned",
        )

    def test_ignores_installments_from_intentions_started_before_range(self):
        self._create_intention("Celular", "5000.00", "2026-08-01", 10)

        result = self.use_case.execute(self.user.id, start="2026-09", end="2026-10")

        self.assertEqual(
            [month["intentions_total"] for month in result["months"]],
            ["0.00", "0.00"],
        )

    def test_counts_intentions_started_inside_range(self):
        self._create_intention("Notebook", "1000.00", "2026-09-01", 2)

        result = self.use_case.execute(self.user.id, start="2026-09", end="2026-10")

        self.assertEqual(
            [month["intentions_total"] for month in result["months"]],
            ["500.00", "500.00"],
        )
