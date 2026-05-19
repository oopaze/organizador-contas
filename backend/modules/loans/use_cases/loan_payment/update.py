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
        self.loan_payment_repository = loan_payment_repository
        self.loan_repository = loan_repository
        self.loan_payment_serializer = loan_payment_serializer

    @transaction.atomic
    def execute(self, payment_id: str, data: dict, user_id: int) -> dict:
        payment = self.loan_payment_repository.get(payment_id, user_id)
        payment.update(data)
        updated = self.loan_payment_repository.update(payment)

        loan = self.loan_repository.get(payment.loan_id, user_id)
        previous_status = loan.status
        loan.recompute_status()
        if loan.status != previous_status:
            self.loan_repository.update(loan)

        return self.loan_payment_serializer.serialize(updated)
