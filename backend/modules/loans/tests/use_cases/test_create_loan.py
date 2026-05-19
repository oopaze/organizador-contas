from decimal import Decimal
from datetime import date
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.loans.domains.loan import LoanDomain
from modules.loans.use_cases.loan.create import CreateLoanUseCase


class TestCreateLoanUseCase(SimpleTestCase):
    def setUp(self):
        self.repo = Mock()
        self.factory = Mock()
        self.serializer = Mock()
        self.use_case = CreateLoanUseCase(
            loan_repository=self.repo,
            loan_factory=self.factory,
            loan_serializer=self.serializer,
        )

    def test_executes_factory_repo_serializer_in_order(self):
        data = {
            "actor_id": 10,
            "principal_amount": "5000",
            "lent_at": date(2026, 1, 1),
        }
        built = LoanDomain(actor_id=10, principal_amount=Decimal("5000"), lent_at=date(2026, 1, 1))
        saved = LoanDomain(id=1, actor_id=10, principal_amount=Decimal("5000"), lent_at=date(2026, 1, 1))
        self.factory.build.return_value = built
        self.repo.create.return_value = saved
        self.serializer.serialize.return_value = {"id": 1}

        result = self.use_case.execute(data, user_id=7)

        self.factory.build.assert_called_once_with(data, 7)
        self.repo.create.assert_called_once_with(built)
        self.serializer.serialize.assert_called_once_with(saved, include_payments=False)
        self.assertEqual(result, {"id": 1})
