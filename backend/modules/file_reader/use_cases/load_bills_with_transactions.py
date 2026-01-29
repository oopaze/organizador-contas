from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.repositories.bill import BillRepository
from modules.file_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.file_reader.serializers.bill import BillSerializer


class LoadBillsWithTransactionsUseCase:
    def __init__(
        self,
        bill_repository: BillRepository,
        bill_sub_transaction_repository: BillSubTransactionRepository,
        bill_serializer: BillSerializer,
    ):
        self.bill_repository = bill_repository
        self.bill_sub_transaction_repository = bill_sub_transaction_repository
        self.bill_serializer = bill_serializer

    def execute(self, bill_id: str) -> BillDomain:
        bill_sub_transactions = self.bill_sub_transaction_repository.get_many_by_bill_id(bill_id)
        bill = self.bill_repository.get(bill_id)
        bill.set_bill_sub_transactions(bill_sub_transactions)
        return self.bill_serializer.serialize(bill)
