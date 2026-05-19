from modules.loans.repositories.loan import LoanRepository


class DeleteLoanUseCase:
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository

    def execute(self, loan_id: str, user_id: int) -> None:
        self.loan_repository.delete(loan_id, user_id)
