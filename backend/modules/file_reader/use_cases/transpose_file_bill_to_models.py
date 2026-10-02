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
        get_or_create_card_bill_use_case=None,
        transaction_repository=None,
        sub_transaction_repository=None,
    ):
        self.bill_repository = bill_repository
        self.bill_factory = bill_factory
        self.bill_serializer = bill_serializer
        self.bill_sub_transaction_repository = bill_sub_transaction_repository
        self.bill_sub_transaction_factory = bill_sub_transaction_factory
        self.file_repository = file_repository
        self.recalculate_amount_use_case = recalculate_amount_use_case
        self.get_or_create_card_bill_use_case = get_or_create_card_bill_use_case
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, file_id: str, user_id: int, create_in_future_months: bool = False, card_id: int = None) -> list[int]:
        file = self.file_repository.get(file_id)
        response = file.get_response()

        if isinstance(response, list):
            return self._execute_for_many(file, response, user_id, create_in_future_months, card_id)
        return self._execute_for_one(file, response, user_id, create_in_future_months, card_id)

    def _persist_bill(self, file: FileDomain, ai_response: dict, user_id: int, card_id: int = None) -> BillDomain:
        """Persists one imported bill, reusing the card's monthly bill when it has no launches."""
        bill = self.bill_factory.build_from_file(file, ai_response)
        bill.card_id = card_id

        if (
            card_id
            and self.get_or_create_card_bill_use_case is not None
            and self.transaction_repository is not None
            and self.sub_transaction_repository is not None
        ):
            due_date = datetime.strptime(str(bill.due_date), "%Y-%m-%d")
            monthly_bill = self.get_or_create_card_bill_use_case.execute(
                user_id, card_id, due_date.year, due_date.month
            )
            has_launches = self.sub_transaction_repository.get_all_by_transaction_id(
                monthly_bill.id, user_id
            )
            if not has_launches:
                self.transaction_repository.attach_file(monthly_bill.id, user_id, file.id)
                target_bill = BillDomain(
                    due_date=bill.due_date,
                    total_amount=monthly_bill.total_amount,
                    bill_identifier=monthly_bill.transaction_identifier,
                    file=file,
                    id=monthly_bill.id,
                    transaction_type=monthly_bill.transaction_type,
                    category=monthly_bill.category,
                    card_id=card_id,
                )
                self._create_sub_transactions(file, target_bill, ai_response)
                self.recalculate_amount_use_case.execute(monthly_bill.id, user_id)
                return target_bill

        saved_bill = self.bill_repository.create(bill, user_id)
        self._create_sub_transactions(file, saved_bill, ai_response)
        return saved_bill

    def _create_sub_transactions(self, file: FileDomain, bill: BillDomain, ai_response: dict):
        bill_sub_transactions = self.bill_sub_transaction_factory.build_many_from_file(
            file, bill, ai_response
        )
        self.bill_sub_transaction_repository.create_many(bill_sub_transactions)

    def _execute_for_one(self, file: FileDomain, response: dict, user_id: int, create_in_future_months: bool = False, card_id: int = None) -> list[int]:
        created_ids = []
        saved_bill = self._persist_bill(file, response, user_id, card_id)
        created_ids.append(saved_bill.id)

        future_transactions = self._get_future_transactions(response, saved_bill) if create_in_future_months else []
        for future_transaction in future_transactions:
            saved_future_bill = self._persist_bill(file, future_transaction, user_id, card_id)
            created_ids.append(saved_future_bill.id)
            self.recalculate_amount_use_case.execute(saved_future_bill.id, user_id)
        return created_ids

    def _get_future_transactions(self, response: dict, bill: BillDomain) -> list:
        base_due_date = datetime.strptime(bill.due_date, "%Y-%m-%d")
        
        future_buckets = {}
        max_offset = 0

        for sub in response.get("transactions", []):
            info = sub.get("installment_info", "")
            
            if not info:
                continue

            try:
                parts = info.replace("installment ", "").split("/")
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
                        "installment_info": f"{current + offset}/{total}",
                    })
            except (ValueError, IndexError):
                continue 

        result = []
        for offset in range(max_offset + 1):
            if offset == 0:
                continue
    
            future_date = base_due_date + relativedelta(months=offset)
            formatted_date = future_date.strftime("%Y-%m-%d")
            
            bill_data = self.bill_serializer.serialize_as_file(bill, formatted_date)
            bill_data["transactions"] = future_buckets.get(offset, [])
            result.append(bill_data)

        return result

    def _execute_for_many(self, file: FileDomain, response: list, user_id: int, create_in_future_months: bool = False, card_id: int = None) -> list[int]:
        created_ids = []
        if response and "despesas" in response[0]:
            logger.info(f"[Transpose] Detected monthly format, flattening {len(response)} months")
            response = self._flatten_monthly_response(response)
            logger.info(f"[Transpose] Flattened to {len(response)} individual items")

        for r in response:
            try:
                saved_bill = self._persist_bill(file, r, user_id, card_id)
                created_ids.append(saved_bill.id)
            except Exception as e:
                logger.warning(f"[Transpose] Skipping item due to error: {e}")
                continue
        return created_ids

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
