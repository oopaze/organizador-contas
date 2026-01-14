from modules.pdf_reader.domains.bill_sub_transaction import BillSubTransactionDomain
from modules.pdf_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.transactions.models import SubTransaction


class BillSubTransactionRepository:
    def __init__(self, model: SubTransaction, bill_sub_transaction_factory: BillSubTransactionFactory):
        self.model = model
        self.bill_sub_transaction_factory = bill_sub_transaction_factory

    def get_many_by_bill_id(self, bill_id: str) -> list[BillSubTransactionDomain]:
        bill_sub_transaction_instances = self.model.objects.filter(transaction_id=bill_id)
        return [
            self.bill_sub_transaction_factory.build_from_model(bill_sub_transaction_instance)
            for bill_sub_transaction_instance in bill_sub_transaction_instances
        ]

    def create(self, bill_sub_transaction: BillSubTransactionDomain) -> BillSubTransactionDomain:
        bill_sub_transaction_instance = self.model.objects.create(
            date=bill_sub_transaction.date,
            description=bill_sub_transaction.description,
            amount=bill_sub_transaction.amount,
            installment_info=bill_sub_transaction.installment_info,
            transaction_id=bill_sub_transaction.bill.id,
        )
        return self.bill_sub_transaction_factory.build_from_model(bill_sub_transaction_instance)
    
    def create_many(self, bill_sub_transactions: list[BillSubTransactionDomain]) -> list[BillSubTransactionDomain]:
        return [
            self.create(bill_sub_transaction) for bill_sub_transaction in bill_sub_transactions
        ]
