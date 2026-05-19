from django.db import transaction

from modules.loans.repositories.loan import LoanRepository
from modules.loans.repositories.loan_payment import LoanPaymentRepository


class DeleteLoanPaymentUseCase:
    def __init__(
        self,
        loan_payment_repository: LoanPaymentRepository,
        loan_repository: LoanRepository,
    ):
        self.loan_payment_repository = loan_payment_repository
        self.loan_repository = loan_repository

    @transaction.atomic
    def execute(self, payment_id: str, user_id: int) -> None:
        payment = self.loan_payment_repository.get(payment_id, user_id)
        self.loan_payment_repository.delete(payment_id)

        loan = self.loan_repository.get(payment.loan_id, user_id)
        previous_status = loan.status
        loan.recompute_status()
        if loan.status != previous_status:
            self.loan_repository.update(loan)
