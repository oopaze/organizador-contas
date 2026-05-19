from django.db import transaction

from modules.loans.repositories.loan import LoanRepository
from modules.loans.repositories.loan_payment import LoanPaymentRepository
from modules.loans.serializers.loan_payment import LoanPaymentSerializer


class UpdateLoanPaymentUseCase:
    def __init__(
        self,
        loan_payment_repository: LoanPaymentRepository,
        loan_repository: LoanRepository,
        loan_payment_serializer: LoanPaymentSerializer,
    ):
        self.payment_repo = loan_payment_repository
        self.loan_repo = loan_repository
        self.serializer = loan_payment_serializer

    @transaction.atomic
    def execute(self, payment_id: str, data: dict, user_id: int) -> dict:
        payment = self.payment_repo.get(payment_id, user_id)
        payment.update(data)
        updated = self.payment_repo.update(payment)

        loan = self.loan_repo.get(payment.loan_id, user_id)
        previous_status = loan.status
        loan.recompute_status()
        if loan.status != previous_status:
            self.loan_repo.update(loan)

        return self.serializer.serialize(updated)
