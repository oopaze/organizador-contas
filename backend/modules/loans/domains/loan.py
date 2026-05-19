from decimal import Decimal


class LoanDomain:
    def __init__(
        self,
        actor_id: int = None,
        actor=None,
        principal_amount=None,
        lent_at=None,
        description: str = "",
        status: str = "active",
        file_id: int = None,
        user_id: int = None,
        id: int = None,
        created_at=None,
        updated_at=None,
        payments: list = None,
    ):
        self.id = id
        self.actor_id = actor_id
        self.actor = actor
        self.principal_amount = (
            Decimal(principal_amount) if principal_amount is not None else None
        )
        self.lent_at = lent_at
        self.description = description or ""
        self.status = status
        self.file_id = file_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.payments = payments or []

    @property
    def total_paid(self) -> Decimal:
        return sum((p.amount for p in self.payments), Decimal("0"))

    @property
    def remaining(self) -> Decimal:
        return (self.principal_amount or Decimal("0")) - self.total_paid

    @property
    def progress_pct(self) -> float:
        if not self.principal_amount or self.principal_amount == 0:
            return 0.0
        ratio = self.total_paid / self.principal_amount
        return float(min(ratio, Decimal("1")) * 100)

    @property
    def is_settled(self) -> bool:
        return self.remaining <= 0

    def update(self, data: dict):
        if "actor_id" in data:
            self.actor_id = data["actor_id"]
        if "principal_amount" in data:
            self.principal_amount = Decimal(data["principal_amount"])
        if "lent_at" in data:
            self.lent_at = data["lent_at"]
        if "description" in data:
            self.description = data["description"] or ""
        if "status" in data:
            self.status = data["status"]
        if "file_id" in data:
            self.file_id = data["file_id"]

    def set_payments(self, payments: list):
        self.payments = payments

    def recompute_status(self):
        """Move ACTIVE → SETTLED automatically when fully paid; reverse if a
        payment is removed and remaining > 0. CANCELLED is never auto-changed.
        """
        if self.status == "cancelled":
            return
        self.status = "settled" if self.is_settled else "active"
