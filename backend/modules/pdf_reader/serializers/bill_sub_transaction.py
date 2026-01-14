from modules.pdf_reader.domains.bill_sub_transaction import BillSubTransactionDomain


class BillSubTransactionSerializer:
    def serialize(self, bill_sub_transaction: BillSubTransactionDomain) -> dict:
        return {
            "id": bill_sub_transaction.id,
            "date": bill_sub_transaction.date,
            "description": bill_sub_transaction.description,
            "amount": bill_sub_transaction.amount,
            "installment_info": bill_sub_transaction.installment_info,
            "created_at": bill_sub_transaction.created_at,
            "updated_at": bill_sub_transaction.updated_at,
        }
