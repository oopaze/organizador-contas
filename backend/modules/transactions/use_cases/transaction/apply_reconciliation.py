from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.types import TransactionCategory
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase


class ApplyReconciliationUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        sub_transaction_repository: SubTransactionRepository,
        recalculate_amount_use_case: RecalculateAmountUseCase,
        get_or_create_card_bill_use_case=None,
    ):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.recalculate_amount_use_case = recalculate_amount_use_case
        self.get_or_create_card_bill_use_case = get_or_create_card_bill_use_case

    def execute(self, data: dict, user_id: int) -> dict:
        merged = 0
        touched_open_bill_ids = set()
        bill, target_bill = self._resolve_absorption(data, user_id)

        for pair in data.get("pairs", []):
            try:
                bill_sub = self.sub_transaction_repository.get(pair["bill_sub_transaction_id"], user_id)
                real_sub = self.sub_transaction_repository.get(pair["real_sub_transaction_id"], user_id)
            except ObjectDoesNotExist:
                continue
            open_bill = self.transaction_repository.get(real_sub.transaction.id, user_id)
            if open_bill.file_id is not None or open_bill.category != TransactionCategory.CREDIT_CARD.name:
                continue

            if bill_sub.actor is None and real_sub.actor is not None:
                bill_sub.update({"actor": real_sub.actor})
            if not bill_sub.user_provided_description and real_sub.user_provided_description:
                bill_sub.update({"user_provided_description": real_sub.user_provided_description})
            if target_bill is not None:
                bill_sub.transaction = target_bill
            self.sub_transaction_repository.update(bill_sub)
            self.sub_transaction_repository.delete(real_sub.id)
            touched_open_bill_ids.add(open_bill.id)
            merged += 1

        categorized = 0
        for item in data.get("categories", []):
            try:
                sub = self.sub_transaction_repository.get(item["sub_transaction_id"], user_id)
            except ObjectDoesNotExist:
                continue
            if sub.category == item["category"]:
                continue
            sub.update({"category": item["category"]})
            self.sub_transaction_repository.update(sub)
            categorized += 1

        if target_bill is not None and bill is not None:
            for sub in self.sub_transaction_repository.get_all_by_transaction_id(bill.id, user_id):
                sub.transaction = target_bill
                self.sub_transaction_repository.update(sub)
            self.transaction_repository.attach_file(target_bill.id, user_id, bill.file_id)
            self.recalculate_amount_use_case.execute(target_bill.id, user_id)
            self.transaction_repository.delete(bill.id, user_id)

        closed_open_bills = []
        unmatched_remaining = 0
        for open_bill_id in touched_open_bill_ids:
            remaining_subs = self.sub_transaction_repository.get_all_by_transaction_id(open_bill_id, user_id)
            if remaining_subs:
                self.recalculate_amount_use_case.execute(open_bill_id, user_id)
                unmatched_remaining += len(remaining_subs)
            else:
                self.transaction_repository.delete(open_bill_id, user_id)
                closed_open_bills.append(open_bill_id)

        return {
            "merged": merged,
            "categorized": categorized,
            "unmatched_remaining": unmatched_remaining,
            "closed_open_bills": closed_open_bills,
            "merged_into_bill_id": target_bill.id if target_bill is not None else None,
        }

    def _resolve_absorption(self, data: dict, user_id: int):
        """Resolves the monthly bill that must absorb the imported bill being reconciled."""
        bill_transaction_id = data.get("bill_transaction_id")
        if not bill_transaction_id or self.get_or_create_card_bill_use_case is None:
            return None, None
        try:
            bill = self.transaction_repository.get(bill_transaction_id, user_id)
        except ObjectDoesNotExist:
            return None, None
        if bill.card_id is None or bill.file_id is None:
            return None, None

        due_date = bill.due_date
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        target_bill = self.get_or_create_card_bill_use_case.execute(
            user_id, bill.card_id, due_date.year, due_date.month
        )
        if target_bill.id == bill.id:
            return None, None
        return bill, target_bill
