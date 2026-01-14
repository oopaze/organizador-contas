from modules.pdf_reader.domains.bill import BillDomain
from modules.pdf_reader.domains.file import FileDomain
from modules.pdf_reader.factories.file import FileFactory
from modules.transactions.models import Transaction


class BillFactory:
    def __init__(self, file_factory: FileFactory):
        self.file_factory = file_factory

    def build_from_file(self, file: FileDomain) -> BillDomain:
        ai_response = file.ai_call.response
        return BillDomain(
            due_date=ai_response["due_date"],
            total_amount=ai_response["total_amount"],
            bill_identifier=ai_response["bill_identifier"],
            file=file,
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
