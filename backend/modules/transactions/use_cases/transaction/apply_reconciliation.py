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
    ):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.recalculate_amount_use_case = recalculate_amount_use_case

    def execute(self, data: dict, user_id: int) -> dict:
        merged = 0
        touched_open_bill_ids = set()

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
        }
