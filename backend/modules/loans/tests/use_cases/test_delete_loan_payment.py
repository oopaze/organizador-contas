from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from modules.loans.domains.loan import LoanDomain
from modules.loans.domains.loan_payment import LoanPaymentDomain
from modules.loans.use_cases.loan_payment.delete import DeleteLoanPaymentUseCase


@patch("django.db.transaction.Atomic.__enter__", return_value=None)
@patch("django.db.transaction.Atomic.__exit__", return_value=False)
class TestDeleteLoanPaymentUseCase(SimpleTestCase):
    def setUp(self):
        self.payment_repo = Mock()
        self.loan_repo = Mock()
        self.use_case = DeleteLoanPaymentUseCase(
            loan_payment_repository=self.payment_repo,
            loan_repository=self.loan_repo,
        )

    def test_reverts_settled_loan_to_active_when_remaining_after_delete(self, _exit, _enter):
        deleted_payment = LoanPaymentDomain(id=2, loan_id=1, amount=Decimal("1000"), paid_at=date(2026, 3, 1))
        loan_after = LoanDomain(
            id=1, user_id=7, actor_id=10,
            principal_amount=Decimal("5000"),
            lent_at=date(2026, 1, 1),
            status="settled",
            payments=[LoanPaymentDomain(id=1, loan_id=1, amount=Decimal("4000"), paid_at=date(2026, 2, 1))],
        )
        self.payment_repo.get.return_value = deleted_payment
        self.loan_repo.get.return_value = loan_after

        self.use_case.execute(payment_id=2, user_id=7)

        self.payment_repo.delete.assert_called_once_with(2)
        self.loan_repo.update.assert_called_once()
        self.assertEqual(self.loan_repo.update.call_args[0][0].status, "active")
