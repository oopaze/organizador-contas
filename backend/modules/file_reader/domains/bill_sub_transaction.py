class BillSubTransactionDomain:
    def __init__(
        self,
        date: str = None,
        description: str = None,
        amount: float = None,
        installment_info: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        bill: "BillDomain" = None,
    ):
        self.date = date
        self.description = description
        self.amount = amount
        self.installment_info = installment_info
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.bill = bill
