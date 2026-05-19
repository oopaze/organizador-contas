from decimal import Decimal
from datetime import date

from django.test import SimpleTestCase

from modules.loans.domains.loan import LoanDomain
from modules.loans.domains.loan_payment import LoanPaymentDomain


class TestLoanDomain(SimpleTestCase):
    def _make_loan(self, principal="5000", payments=None):
        return LoanDomain(
            id=1,
            actor_id=10,
            principal_amount=Decimal(principal),
            lent_at=date(2026, 1, 1),
            description="",
            status="active",
            payments=payments or [],
        )

    def _payment(self, amount):
        return LoanPaymentDomain(
            id=1, loan_id=1, amount=Decimal(amount), paid_at=date(2026, 2, 1), note=""
        )

    def test_total_paid_sums_payments(self):
        loan = self._make_loan(payments=[self._payment("1000"), self._payment("500")])
        self.assertEqual(loan.total_paid, Decimal("1500"))

    def test_remaining_subtracts_total_paid_from_principal(self):
        loan = self._make_loan(payments=[self._payment("1000")])
        self.assertEqual(loan.remaining, Decimal("4000"))

    def test_progress_pct_capped_at_100(self):
        loan = self._make_loan(payments=[self._payment("6000")])
        self.assertEqual(loan.progress_pct, 100.0)

    def test_progress_pct_when_no_payments(self):
        loan = self._make_loan()
        self.assertEqual(loan.progress_pct, 0.0)

    def test_is_settled_when_remaining_zero_or_negative(self):
        self.assertTrue(self._make_loan(payments=[self._payment("5000")]).is_settled)
        self.assertTrue(self._make_loan(payments=[self._payment("5500")]).is_settled)
        self.assertFalse(self._make_loan(payments=[self._payment("100")]).is_settled)

    def test_recompute_status_moves_active_to_settled_when_fully_paid(self):
        loan = self._make_loan(payments=[self._payment("5000")])
        loan.status = "active"
        loan.recompute_status()
        self.assertEqual(loan.status, "settled")

    def test_recompute_status_reverts_settled_to_active_when_remaining(self):
        loan = self._make_loan(payments=[self._payment("100")])
        loan.status = "settled"
        loan.recompute_status()
        self.assertEqual(loan.status, "active")

    def test_recompute_status_leaves_cancelled_alone(self):
        loan = self._make_loan(payments=[self._payment("5000")])
        loan.status = "cancelled"
        loan.recompute_status()
        self.assertEqual(loan.status, "cancelled")
