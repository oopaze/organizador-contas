from modules.loans.repositories.loan_payment import LoanPaymentRepository
from modules.loans.serializers.loan_payment import LoanPaymentSerializer


class ListLoanPaymentsUseCase:
    def __init__(self, loan_payment_repository: LoanPaymentRepository, loan_payment_serializer: LoanPaymentSerializer):
        self.repo = loan_payment_repository
        self.serializer = loan_payment_serializer

    def execute(
        self,
        user_id: int,
        loan_id: str | None = None,
        paid_at_month: int | None = None,
        paid_at_year: int | None = None,
    ) -> list[dict]:
        filters = {}
        if loan_id:
            filters["loan_id"] = loan_id
        if paid_at_month:
            filters["paid_at__month"] = paid_at_month
        if paid_at_year:
            filters["paid_at__year"] = paid_at_year
        payments = self.repo.get_all(user_id, filters)
        return self.serializer.serialize_many(payments)
