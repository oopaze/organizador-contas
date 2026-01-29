from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.serializers.bill_sub_transaction import BillSubTransactionSerializer


class BillSerializer:
    def __init__(self, bill_sub_transaction_serializer: BillSubTransactionSerializer):
        self.bill_sub_transaction_serializer = bill_sub_transaction_serializer

    def serialize(self, bill: BillDomain, include_transactions: bool = True) -> dict:
        data = {
            "id": bill.id,
            "due_date": bill.due_date,
            "total_amount": bill.total_amount,
            "bill_identifier": bill.bill_identifier,
            "file": bill.file.url if bill.file else None,
            "created_at": bill.created_at,
            "updated_at": bill.updated_at,
        }

        if include_transactions:
            data["bill_sub_transactions"] = [
                self.bill_sub_transaction_serializer.serialize(bill_sub_transaction)
                for bill_sub_transaction in bill.bill_sub_transactions
            ]

        return data
