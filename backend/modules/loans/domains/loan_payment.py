from datetime import date, datetime
from decimal import Decimal


def _coerce_date(value):
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(value, "%Y-%m-%d").date()


class LoanPaymentDomain:
    def __init__(
        self,
        amount=None,
        paid_at=None,
        loan_id: int = None,
        note: str = "",
        file_id: int = None,
        id: int = None,
        created_at=None,
        updated_at=None,
    ):
        self.id = id
        self.loan_id = loan_id
        self.amount = Decimal(amount) if amount is not None else None
        self.paid_at = _coerce_date(paid_at)
        self.note = note or ""
        self.file_id = file_id
        self.created_at = created_at
        self.updated_at = updated_at

    def update(self, data: dict):
        if "amount" in data:
            self.amount = Decimal(data["amount"])
        if "paid_at" in data:
            self.paid_at = _coerce_date(data["paid_at"])
        if "note" in data:
            self.note = data["note"] or ""
        if "file_id" in data:
            self.file_id = data["file_id"]
