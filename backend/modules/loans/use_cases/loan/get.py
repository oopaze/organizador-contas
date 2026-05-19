from modules.loans.repositories.loan import LoanRepository
from modules.loans.serializers.loan import LoanSerializer


class GetLoanUseCase:
    def __init__(self, loan_repository: LoanRepository, loan_serializer: LoanSerializer):
        self.loan_repository = loan_repository
        self.loan_serializer = loan_serializer

    def execute(self, loan_id: str, user_id: int) -> dict:
        loan = self.loan_repository.get(loan_id, user_id)
        return self.loan_serializer.serialize(loan, include_payments=True)
