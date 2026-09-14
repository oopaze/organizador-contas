from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import TransactionDomain
from modules.transactions.use_cases.transaction.ensure_salary import EnsureMonthlySalaryUseCase
from modules.userdata.domains.profile import ProfileDomain


class TestEnsureMonthlySalaryUseCase(SimpleTestCase):
    def setUp(self):
        self.transaction_repository = Mock()
        self.transaction_factory = Mock()
        self.transaction_serializer = Mock()
        self.profile_repository = Mock()

        self.use_case = EnsureMonthlySalaryUseCase(
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            profile_repository=self.profile_repository,
        )

    def test_skips_when_salary_not_configured(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain()

        result = self.use_case.execute(7, "2026-09")

        self.assertEqual(result, {"salary": None})
        self.transaction_repository.filter.assert_not_called()
        self.transaction_repository.create.assert_not_called()

    def test_creates_past_salary_as_paid(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(
            salary="5000", salary_day=5
        )
        self.transaction_repository.filter.return_value = []
        self.transaction_factory.build.return_value = TransactionDomain(
            total_amount="5000", user_id=7
        )
        self.transaction_repository.create.return_value = TransactionDomain(
            id=99, total_amount="5000", user_id=7
        )
        self.transaction_serializer.serialize.return_value = {"id": 99}

        result = self.use_case.execute(7, "2020-09")

        built = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built["transaction_identifier"], "Salário 09/2020")
        self.assertEqual(built["due_date"], "2020-09-05")
        self.assertEqual(built["transaction_type"], "incoming")
        self.assertTrue(built["is_salary"])
        self.assertEqual(built["paid_at"], "2020-09-05")
        self.assertEqual(result, {"salary": {"id": 99}})

    def test_creates_future_salary_as_unpaid(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(
            salary="5000", salary_day=5
        )
        self.transaction_repository.filter.return_value = []
        self.transaction_factory.build.return_value = TransactionDomain(
            total_amount="5000", user_id=7
        )
        self.transaction_repository.create.return_value = TransactionDomain(
            id=100, total_amount="5000", user_id=7
        )
        self.transaction_serializer.serialize.return_value = {"id": 100}

        self.use_case.execute(7, "2099-01")

        built = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built["due_date"], "2099-01-05")
        self.assertIsNone(built["paid_at"])

    def test_clamps_day_to_month_end(self):
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(
            salary="5000", salary_day=31
        )
        self.transaction_repository.filter.return_value = []
        self.transaction_factory.build.return_value = TransactionDomain(
            total_amount="5000", user_id=7
        )
        self.transaction_repository.create.return_value = TransactionDomain(
            id=101, total_amount="5000", user_id=7
        )
        self.transaction_serializer.serialize.return_value = {"id": 101}

        self.use_case.execute(7, "2026-02")

        built = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built["due_date"], "2026-02-28")

    def test_updates_unpaid_existing_salary_amount(self):
        existing = TransactionDomain(id=50, total_amount="4000", user_id=7)
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(
            salary="5500", salary_day=5
        )
        self.transaction_repository.filter.return_value = [existing]
        self.transaction_repository.update.return_value = existing
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2099-01")

        self.assertEqual(str(existing.total_amount), "5500")
        self.transaction_repository.update.assert_called_once_with(existing)
        self.transaction_repository.create.assert_not_called()

    def test_keeps_paid_salary_untouched(self):
        existing = TransactionDomain(
            id=50, total_amount="4000", user_id=7, paid_at="2026-09-05"
        )
        self.profile_repository.get_by_user_id.return_value = ProfileDomain(
            salary="5500", salary_day=5
        )
        self.transaction_repository.filter.return_value = [existing]
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-09")

        self.transaction_repository.update.assert_not_called()
        self.transaction_repository.create.assert_not_called()
