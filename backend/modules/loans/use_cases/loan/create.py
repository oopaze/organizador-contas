from modules.loans.factories.loan import LoanFactory
from modules.loans.repositories.loan import LoanRepository
from modules.loans.serializers.loan import LoanSerializer


class CreateLoanUseCase:
    def __init__(
        self,
        loan_repository: LoanRepository,
        loan_factory: LoanFactory,
        loan_serializer: LoanSerializer,
    ):
        self.loan_repository = loan_repository
        self.loan_factory = loan_factory
        self.loan_serializer = loan_serializer

    def execute(self, data: dict, user_id: int) -> dict:
        loan = self.loan_factory.build(data, user_id)
        saved = self.loan_repository.create(loan)
        return self.loan_serializer.serialize(saved, include_payments=False)
