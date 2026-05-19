from modules.loans.repositories.loan import LoanRepository
from modules.loans.serializers.loan import LoanSerializer


class ListLoansUseCase:
    def __init__(self, loan_repository: LoanRepository, loan_serializer: LoanSerializer):
        self.loan_repository = loan_repository
        self.loan_serializer = loan_serializer

    def execute(self, user_id: int, filters: dict | None = None) -> list[dict]:
        loans = self.loan_repository.get_all(user_id, filters or {})
        return self.loan_serializer.serialize_many(loans)
