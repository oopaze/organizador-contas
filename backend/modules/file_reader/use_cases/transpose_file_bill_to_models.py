import logging

from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.bill import BillFactory
from modules.file_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.file_reader.repositories.bill import BillRepository
from modules.file_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.file_reader.repositories.file import FileRepository

logger = logging.getLogger(__name__)


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

    def _flatten_monthly_response(self, response: list) -> list:
        """
        Flatten monthly format responses into individual bill items.

        Input format (monthly):
        [
            {"ano": 2026, "mes": "Janeiro", "despesas": [{"nome": "Aluguel", "valor_meu": 800}, ...]},
            {"ano": 2025, "mes": "Dezembro", "despesas": [...]},
        ]

        Output format (flat):
        [
            {"due_date": "2026-01-01", "bill_identifier": "Aluguel", "total_amount": 800},
            ...
        ]
        """
        flattened = []

        for month_data in response:
            # Check if this is monthly format (has ano/mes/despesas)
            if "despesas" in month_data and "ano" in month_data:
                ano = month_data.get("ano")
                mes = month_data.get("mes")
                despesas = month_data.get("despesas", [])

                for despesa in despesas:
                    # Add ano/mes to each despesa for date calculation
                    despesa_with_date = {**despesa, "ano": ano, "mes": mes}
                    flattened.append(despesa_with_date)
            else:
                # Already in flat format
                flattened.append(month_data)

        return flattened

    def execute(self, file_id: str, user_id: int):
        file = self.file_repository.get(file_id)

        if response := file.get_response():
            if isinstance(response, list):
                # Check if response is in monthly format and flatten it
                if response and "despesas" in response[0]:
                    logger.info(f"[Transpose] Detected monthly format, flattening {len(response)} months")
                    response = self._flatten_monthly_response(response)
                    logger.info(f"[Transpose] Flattened to {len(response)} individual items")

                for r in response:
                    try:
                        bill = self.bill_factory.build_from_file(file, r)
                        saved_bill = self.bill_repository.create(bill, user_id)
                        bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(file, saved_bill, r)
                        self.bill_sub_transaction_repository.create_many(bill_sub_transactions)
                    except Exception as e:
                        logger.warning(f"[Transpose] Skipping item due to error: {e}")
                        continue
                return

        bill = self.bill_factory.build_from_file(file)
        saved_bill = self.bill_repository.create(bill, user_id)
        bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(file, saved_bill)
        self.bill_sub_transaction_repository.create_many(bill_sub_transactions)
