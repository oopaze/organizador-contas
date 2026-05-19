from modules.loans.repositories.loan import LoanRepository


class LoanStatsUseCase:
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository

    def execute(self, user_id: int) -> dict:
        return self.loan_repository.stats(user_id)
