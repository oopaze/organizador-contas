from modules.loans.domains.loan import LoanDomain
from modules.loans.serializers.loan_payment import LoanPaymentSerializer


class LoanSerializer:
    def __init__(self, loan_payment_serializer: LoanPaymentSerializer):
        self.loan_payment_serializer = loan_payment_serializer

    def serialize(self, loan: LoanDomain, include_payments: bool = True) -> dict:
        data = {
            "id": loan.id,
            "actor_id": loan.actor_id,
            "principal_amount": str(loan.principal_amount),
            "lent_at": loan.lent_at.isoformat() if loan.lent_at else None,
            "description": loan.description,
            "status": loan.status,
            "file_id": loan.file_id,
            "total_paid": str(loan.total_paid),
            "remaining": str(loan.remaining),
            "progress_pct": loan.progress_pct,
            "is_settled": loan.is_settled,
            "created_at": loan.created_at.isoformat() if loan.created_at else None,
            "updated_at": loan.updated_at.isoformat() if loan.updated_at else None,
        }
        if include_payments:
            data["payments"] = self.loan_payment_serializer.serialize_many(loan.payments)
        return data

    def serialize_many(self, loans: list[LoanDomain]) -> list[dict]:
        return [self.serialize(loan) for loan in loans]
