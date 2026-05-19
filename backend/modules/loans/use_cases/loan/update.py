from modules.loans.repositories.loan import LoanRepository
from modules.loans.serializers.loan import LoanSerializer


class UpdateLoanUseCase:
    def __init__(self, loan_repository: LoanRepository, loan_serializer: LoanSerializer):
        self.loan_repository = loan_repository
        self.loan_serializer = loan_serializer

    def execute(self, loan_id: str, data: dict, user_id: int) -> dict:
        loan = self.loan_repository.get(loan_id, user_id)
        loan.update(data)
        loan.recompute_status()
        saved = self.loan_repository.update(loan)
        return self.loan_serializer.serialize(saved, include_payments=True)
