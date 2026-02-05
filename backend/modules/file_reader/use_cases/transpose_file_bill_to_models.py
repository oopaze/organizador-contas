import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.bill import BillFactory
from modules.file_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.file_reader.repositories.bill import BillRepository
from modules.file_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.serializers.bill import BillSerializer
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase

logger = logging.getLogger(__name__)


class TransposeFileBillToModelsUseCase:
    def __init__(
        self,
        bill_repository: BillRepository,
        bill_factory: BillFactory,
        bill_serializer: BillSerializer,
        bill_sub_transaction_repository: BillSubTransactionRepository,
        bill_sub_transaction_factory: BillSubTransactionFactory,
        file_repository: FileRepository,
        recalculate_amount_use_case: RecalculateAmountUseCase,
    ):
        self.bill_repository = bill_repository
        self.bill_factory = bill_factory
        self.bill_serializer = bill_serializer
        self.bill_sub_transaction_repository = bill_sub_transaction_repository
        self.bill_sub_transaction_factory = bill_sub_transaction_factory
        self.file_repository = file_repository
        self.recalculate_amount_use_case = recalculate_amount_use_case

    def execute(self, file_id: str, user_id: int, create_in_future_months: bool = False):
        file = self.file_repository.get(file_id)
        response = file.get_response()

        if isinstance(response, list):
            return self._execute_for_many(file, response, user_id, create_in_future_months)
        return self._execute_for_one(file, response, user_id, create_in_future_months)

    def _execute_for_one(self, file: FileDomain, response: dict, user_id: int, create_in_future_months: bool = False):
        bill = self.bill_factory.build_from_file(file, response)
        saved_bill = self.bill_repository.create(bill, user_id)
        bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(file, saved_bill, response)
        self.bill_sub_transaction_repository.create_many(bill_sub_transactions)

        future_transactions = self._get_future_transactions(response, saved_bill) if create_in_future_months else []
        for future_transaction in future_transactions:
            bill = self.bill_factory.build_from_file(file, future_transaction)
            saved_bill = self.bill_repository.create(bill, user_id)
            bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(file, saved_bill, ai_response=future_transaction)
            self.bill_sub_transaction_repository.create_many(bill_sub_transactions)
            self.recalculate_amount_use_case.execute(saved_bill.id, user_id)

    def _get_future_transactions(self, response: dict, bill: BillDomain) -> list:
        base_due_date = datetime.strptime(bill.due_date, "%Y-%m-%d")
        
        future_buckets = {}
        max_offset = 0

        for sub in response.get("transactions", []):
            info = sub.get("installment_info", "")
            
            if "of" not in info or "not" in info:
                continue

            try:
                parts = info.replace("installment ", "").split(" of ")
                current, total = map(int, parts)
                remaining = total - current
                max_offset = max(max_offset, remaining)

                for offset in range(remaining + 1):
                    if offset not in future_buckets:
                        future_buckets[offset] = []
                    
                    future_buckets[offset].append({
                        "date": sub["date"],
                        "description": sub["description"],
                        "amount": sub["amount"],
                        "installment_info": f"installment {current + offset} of {total}",
                    })
            except (ValueError, IndexError):
                continue 

        result = []
        for offset in range(max_offset + 1):
            future_date = base_due_date + relativedelta(months=offset)
            formatted_date = future_date.strftime("%Y-%m-%d")
            
            bill_data = self.bill_serializer.serialize_as_file(bill, formatted_date)
            bill_data["transactions"] = future_buckets.get(offset, [])
            result.append(bill_data)

        return result

    def _execute_for_many(self, file: FileDomain, response: list, user_id: int):
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

    def _flatten_monthly_response(self, response: list) -> list:
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
