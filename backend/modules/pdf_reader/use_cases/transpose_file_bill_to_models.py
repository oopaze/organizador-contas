from modules.pdf_reader.domains.file import FileDomain
from modules.pdf_reader.factories.bill import BillFactory
from modules.pdf_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.pdf_reader.repositories.bill import BillRepository
from modules.pdf_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.pdf_reader.repositories.file import FileRepository


class TransposeFileBillToModelsUseCase:
    def __init__(
        self,
        bill_repository: BillRepository,
        bill_factory: BillFactory,
        bill_sub_transaction_repository: BillSubTransactionRepository,
        bill_sub_transaction_factory: BillSubTransactionFactory,
        file_repository: FileRepository,
    ):
        self.bill_repository = bill_repository
        self.bill_factory = bill_factory
        self.bill_sub_transaction_repository = bill_sub_transaction_repository
        self.bill_sub_transaction_factory = bill_sub_transaction_factory
        self.file_repository = file_repository

    def execute(self, file_id: str, user_id: int):
        file = self.file_repository.get(file_id)
        bill = self.bill_factory.build_from_file(file)
        saved_bill = self.bill_repository.create(bill, user_id)

        bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(file, saved_bill)
        self.bill_sub_transaction_repository.create_many(bill_sub_transactions)
