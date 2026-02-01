from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.file import FileFactory
from modules.transactions.models import Transaction


class BillFactory:
    def __init__(self, file_factory: FileFactory):
        self.file_factory = file_factory

    def build_from_file(self, file: FileDomain, ai_response: dict = None) -> BillDomain:
        if ai_response is None:
            ai_response = file.ai_call.response

        # Determine transaction_type based on is_income flag
        is_income = ai_response.get("is_income", False)
        transaction_type = "incoming" if is_income else "outgoing"

        return BillDomain(
            due_date=ai_response["due_date"],
            total_amount=ai_response["total_amount"],
            bill_identifier=ai_response["bill_identifier"],
            file=file,
            transaction_type=transaction_type,
        )

    def build_from_model(self, model: Transaction) -> BillDomain:
        return BillDomain(
            due_date=model.due_date,
            total_amount=model.total_amount,
            bill_identifier=model.transaction_identifier,
            file=self.file_factory.build_from_model(model.file),
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
