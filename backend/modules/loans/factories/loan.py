from modules.loans.domains.loan import LoanDomain
from modules.loans.factories.loan_payment import LoanPaymentFactory
from modules.loans.models import Loan


class LoanFactory:
    def __init__(self, loan_payment_factory: LoanPaymentFactory):
        self.loan_payment_factory = loan_payment_factory

    def build_from_model(self, model: Loan, include_payments: bool = False) -> LoanDomain:
        loan = LoanDomain(
            id=model.id,
            actor_id=model.actor_id,
            principal_amount=model.principal_amount,
            lent_at=model.lent_at,
            description=model.description,
            status=model.status,
            file_id=model.file_id,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        if include_payments:
            payments = [
                self.loan_payment_factory.build_from_model(p)
                for p in model.payments.exclude(deleted_at__isnull=False)
            ]
            loan.set_payments(payments)
        return loan

    def build(self, data: dict, user_id: int) -> LoanDomain:
        return LoanDomain(
            actor_id=data["actor_id"],
            principal_amount=data["principal_amount"],
            lent_at=data["lent_at"],
            description=data.get("description", ""),
            status=data.get("status", "active"),
            file_id=data.get("file_id"),
            user_id=user_id,
        )
