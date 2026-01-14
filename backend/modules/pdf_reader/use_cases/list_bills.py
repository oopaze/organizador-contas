from typing import List

from modules.pdf_reader.repositories.bill import BillRepository
from modules.pdf_reader.serializers.bill import BillSerializer


class ListBillsUseCase:
    def __init__(
        self,
        bill_repository: BillRepository,
        bill_serializer: BillSerializer,
    ):
        self.bill_repository = bill_repository
        self.bill_serializer = bill_serializer

    def execute(self) -> List[dict]:
        bills = self.bill_repository.get_all()
        return [
            self.bill_serializer.serialize(bill, include_transactions=False)
            for bill in bills
        ]

