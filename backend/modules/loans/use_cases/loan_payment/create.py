from django.db import transaction

from modules.loans.factories.loan_payment import LoanPaymentFactory
from modules.loans.repositories.loan import LoanRepository
from modules.loans.repositories.loan_payment import LoanPaymentRepository
from modules.loans.serializers.loan_payment import LoanPaymentSerializer


class CreateLoanPaymentUseCase:
    def __init__(
        self,
        loan_payment_repository: LoanPaymentRepository,
        loan_repository: LoanRepository,
        loan_payment_factory: LoanPaymentFactory,
        loan_payment_serializer: LoanPaymentSerializer,
    ):
        self.loan_payment_repository = loan_payment_repository
        self.loan_repository = loan_repository
        self.loan_payment_factory = loan_payment_factory
        self.loan_payment_serializer = loan_payment_serializer

    @transaction.atomic
    def execute(self, data: dict, user_id: int) -> dict:
        loan = self.loan_repository.get(data["loan_id"], user_id)
        if loan.status != "active":
            raise ValueError("Empréstimo não está ativo")

        payment_domain = self.loan_payment_factory.build(data)
        saved_payment = self.loan_payment_repository.create(payment_domain)

        loan.payments = loan.payments + [saved_payment]
        previous_status = loan.status
        loan.recompute_status()
        if loan.status != previous_status:
            self.loan_repository.update(loan)

        return self.loan_payment_serializer.serialize(saved_payment)
