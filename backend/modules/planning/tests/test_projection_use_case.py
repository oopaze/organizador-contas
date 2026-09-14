from datetime import date
from unittest.mock import Mock

from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase

from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.use_cases.intention.projection import ProjectionUseCase
from modules.userdata.domains.profile import ProfileDomain


class TestProjectionUseCase(SimpleTestCase):
    def setUp(self):
        self.intention_repository = Mock()
        self.profile_repository = Mock()
        self.use_case = ProjectionUseCase(self.intention_repository, self.profile_repository)

    def test_sums_installments_across_months(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(salary="5000")
        self.intention_repository.filter.return_value = [
            PurchaseIntentionDomain(id=1, amount="3500", month=date(2026, 10, 1), installments=4),
            PurchaseIntentionDomain(id=2, amount="100", month=date(2026, 9, 1), installments=3),
        ]

        result = self.use_case.execute(7, start="2026-09", end="2026-12")

        months = result["months"]
        self.assertEqual(
            [month["month"] for month in months],
            ["2026-09", "2026-10", "2026-11", "2026-12"],
        )
        self.assertEqual(
            [month["intentions_total"] for month in months],
            ["33.33", "908.33", "908.34", "875.00"],
        )
        self.assertEqual(months[0]["salary"], "5000.00")
        self.assertEqual(months[0]["leftover"], "4966.67")
        self.assertEqual(months[3]["leftover"], "4125.00")
        filters = self.intention_repository.filter.call_args[0][0]
        self.assertEqual(filters, {"user_id": 7, "status": "planned"})

    def test_defaults_to_twelve_months(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(salary="5000")
        self.intention_repository.filter.return_value = []

        result = self.use_case.execute(7, start="2026-09")

        self.assertEqual(result["total_months"], 12)
        self.assertEqual(result["months"][-1]["month"], "2027-08")

    def test_intention_outside_window_counts_zero(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(salary="3000")
        self.intention_repository.filter.return_value = [
            PurchaseIntentionDomain(id=1, amount="600", month=date(2027, 5, 1), installments=2)
        ]

        result = self.use_case.execute(7, start="2026-09", end="2026-10")

        self.assertEqual([month["intentions_total"] for month in result["months"]], ["0.00", "0.00"])
        self.assertEqual(result["months"][0]["leftover"], "3000.00")

    def test_missing_profile_means_zero_salary(self):
        self.profile_repository.get_by_user_id.side_effect = ObjectDoesNotExist
        self.intention_repository.filter.return_value = []

        result = self.use_case.execute(7, start="2026-09", end="2026-09")

        self.assertEqual(result["months"][0]["salary"], "0.00")

    def test_invalid_month_raises(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(7, start="setembro")
