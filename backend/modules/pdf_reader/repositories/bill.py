from typing import List

from modules.pdf_reader.domains.bill import BillDomain
from modules.pdf_reader.factories.bill import BillFactory
from modules.transactions.models import Transaction


class BillRepository:
    def __init__(self, model: Transaction, bill_factory: BillFactory):
        self.model = model
        self.bill_factory = bill_factory

    def get(self, bill_id: str) -> BillDomain:
        bill_instance = self.model.objects.get(id=bill_id)
        return self.bill_factory.build_from_model(bill_instance)

    def get_all(self) -> List[BillDomain]:
        bill_instances = self.model.objects.all()
        return [self.bill_factory.build_from_model(bill) for bill in bill_instances]

    def create(self, bill: BillDomain, user_id: int) -> BillDomain:
        bill_instance = self.model.objects.create(
            due_date=bill.due_date,
            total_amount=bill.total_amount,
            transaction_identifier=bill.bill_identifier,
            file_id=bill.file.id,
            transaction_type="outgoing",
            user_id=user_id,
        )
        return self.bill_factory.build_from_model(bill_instance)
