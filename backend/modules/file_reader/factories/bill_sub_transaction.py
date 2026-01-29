from modules.transactions.models import SubTransaction
from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.bill_sub_transaction import BillSubTransactionDomain
from modules.file_reader.domains.file import FileDomain


class BillSubTransactionFactory:
    def build_many_from_file(self, file: FileDomain, bill: BillDomain) -> BillSubTransactionDomain:
        ai_response = file.ai_call.response
        transactions = ai_response["transactions"]
        return [
            BillSubTransactionDomain(
                date=transaction["date"],
                description=transaction["description"],
                amount=transaction["amount"],
                installment_info=transaction["installment_info"],
                bill=bill,
            )
            for transaction in transactions
        ]

    def build_from_model(self, model: SubTransaction) -> BillSubTransactionDomain:
        return BillSubTransactionDomain(
            date=model.date,
            description=model.description,
            amount=model.amount,
            installment_info=model.installment_info,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            bill=model.transaction,
        )
