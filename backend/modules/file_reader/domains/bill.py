from modules.file_reader.domains.bill_sub_transaction import BillSubTransactionDomain
from modules.file_reader.domains.file import FileDomain


class BillDomain:
    def __init__(
        self,
        due_date: str = None,
        total_amount: float = None,
        bill_identifier: str = None,
        file: FileDomain = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        bill_sub_transactions: list[BillSubTransactionDomain] = [],
        transaction_type: str = "outgoing",
        main_transaction_id: int = None,
        category: str = None,
    ):
        self.due_date = due_date
        self.total_amount = total_amount
        self.bill_identifier = bill_identifier
        self.file = file
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.bill_sub_transactions = bill_sub_transactions
        self.transaction_type = transaction_type
        self.main_transaction_id = main_transaction_id
        self.category = category

    def set_bill_sub_transactions(self, bill_sub_transactions: list[BillSubTransactionDomain]):
        self.bill_sub_transactions = bill_sub_transactions
