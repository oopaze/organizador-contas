from modules.loans.domains.loan_payment import LoanPaymentDomain


class LoanPaymentSerializer:
    def serialize(self, payment: LoanPaymentDomain) -> dict:
        return {
            "id": payment.id,
            "loan_id": payment.loan_id,
            "amount": str(payment.amount),
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
            "note": payment.note,
            "file_id": payment.file_id,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
        }

    def serialize_many(self, payments: list[LoanPaymentDomain]) -> list[dict]:
        return [self.serialize(p) for p in payments]
