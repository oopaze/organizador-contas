from modules.loans.repositories.loan_payment import LoanPaymentRepository
from modules.loans.serializers.loan_payment import LoanPaymentSerializer


class GetLoanPaymentUseCase:
    def __init__(self, loan_payment_repository: LoanPaymentRepository, loan_payment_serializer: LoanPaymentSerializer):
        self.loan_payment_repository = loan_payment_repository
        self.loan_payment_serializer = loan_payment_serializer

    def execute(self, payment_id: str, user_id: int) -> dict:
        return self.loan_payment_serializer.serialize(self.loan_payment_repository.get(payment_id, user_id))
