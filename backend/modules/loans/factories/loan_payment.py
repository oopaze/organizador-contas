from modules.loans.domains.loan_payment import LoanPaymentDomain
from modules.loans.models import LoanPayment


class LoanPaymentFactory:
    def build_from_model(self, model: LoanPayment) -> LoanPaymentDomain:
        return LoanPaymentDomain(
            id=model.id,
            loan_id=model.loan_id,
            amount=model.amount,
            paid_at=model.paid_at,
            note=model.note,
            file_id=model.file_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def build(self, data: dict) -> LoanPaymentDomain:
        return LoanPaymentDomain(
            loan_id=data["loan_id"],
            amount=data["amount"],
            paid_at=data["paid_at"],
            note=data.get("note", ""),
            file_id=data.get("file_id"),
        )
