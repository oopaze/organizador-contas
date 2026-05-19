from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from modules.loans.domains.loan import LoanDomain
from modules.loans.domains.loan_payment import LoanPaymentDomain
from modules.loans.use_cases.loan_payment.create import CreateLoanPaymentUseCase


@patch("django.db.transaction.Atomic.__enter__", return_value=None)
@patch("django.db.transaction.Atomic.__exit__", return_value=False)
class TestCreateLoanPaymentUseCase(SimpleTestCase):
    def setUp(self):
        self.payment_repo = Mock()
        self.loan_repo = Mock()
        self.payment_factory = Mock()
        self.payment_serializer = Mock()
        self.use_case = CreateLoanPaymentUseCase(
            loan_payment_repository=self.payment_repo,
            loan_repository=self.loan_repo,
            loan_payment_factory=self.payment_factory,
            loan_payment_serializer=self.payment_serializer,
        )

    def _loan(self, principal="5000", payments=None, status="active"):
        return LoanDomain(
            id=1, user_id=7, actor_id=10,
            principal_amount=Decimal(principal),
            lent_at=date(2026, 1, 1),
            status=status,
            payments=payments or [],
        )

    def test_creates_payment_and_keeps_loan_active_when_partial(self, _exit, _enter):
        loan = self._loan(payments=[LoanPaymentDomain(id=1, loan_id=1, amount=Decimal("1000"), paid_at=date(2026, 2, 1))])
        new_payment = LoanPaymentDomain(loan_id=1, amount=Decimal("500"), paid_at=date(2026, 3, 1))
        saved_payment = LoanPaymentDomain(id=2, loan_id=1, amount=Decimal("500"), paid_at=date(2026, 3, 1))
        self.loan_repo.get.return_value = loan
        self.payment_factory.build.return_value = new_payment
        self.payment_repo.create.return_value = saved_payment
        self.payment_serializer.serialize.return_value = {"id": 2}

        result = self.use_case.execute({"loan_id": 1, "amount": "500", "paid_at": date(2026, 3, 1)}, user_id=7)

        self.payment_repo.create.assert_called_once_with(new_payment)
        self.loan_repo.update.assert_not_called()
        self.assertEqual(result, {"id": 2})

    def test_flips_loan_to_settled_when_payment_completes(self, _exit, _enter):
        loan = self._loan(payments=[LoanPaymentDomain(id=1, loan_id=1, amount=Decimal("4000"), paid_at=date(2026, 2, 1))])
        new_payment = LoanPaymentDomain(loan_id=1, amount=Decimal("1000"), paid_at=date(2026, 3, 1))
        saved_payment = LoanPaymentDomain(id=2, loan_id=1, amount=Decimal("1000"), paid_at=date(2026, 3, 1))
        self.loan_repo.get.return_value = loan
        self.payment_factory.build.return_value = new_payment
        self.payment_repo.create.return_value = saved_payment
        self.payment_serializer.serialize.return_value = {"id": 2}

        self.use_case.execute({"loan_id": 1, "amount": "1000", "paid_at": date(2026, 3, 1)}, user_id=7)

        self.loan_repo.update.assert_called_once()
        updated_loan = self.loan_repo.update.call_args[0][0]
        self.assertEqual(updated_loan.status, "settled")

    def test_raises_when_loan_not_active(self, _exit, _enter):
        loan = self._loan(status="cancelled")
        self.loan_repo.get.return_value = loan

        with self.assertRaises(ValueError) as cm:
            self.use_case.execute({"loan_id": 1, "amount": "500", "paid_at": date(2026, 3, 1)}, user_id=7)
        self.assertIn("não está ativo", str(cm.exception).lower())
