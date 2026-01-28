from modules.transactions.repositories import TransactionRepository, SubTransactionRepository
from modules.transactions.domains import SubTransactionDomain, TransactionDomain


class TransactionStatsUseCase:
    def __init__(self, transaction_repository: TransactionRepository, sub_transaction_repository: SubTransactionRepository):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, user_id: int, due_date: str) -> dict:
        filters = {"user_id": user_id}
        if due_date:
            filters["due_date__month"] = due_date.split("-")[1]
            filters["due_date__year"] = due_date.split("-")[0]

        transactions = self.transaction_repository.filter(filters)
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_ids([transaction.id for transaction in transactions])
        return self.calculate_stats(transactions, sub_transactions)

    def calculate_stats(self, transactions: list[TransactionDomain], sub_transactions: list[SubTransactionDomain]) -> dict:
        incoming_total = sum([transaction.total_amount for transaction in transactions if transaction.transaction_type == "incoming"])
        outgoing_total = sum([transaction.total_amount for transaction in transactions if transaction.transaction_type == "outgoing"])
        balance = incoming_total - outgoing_total
        outgoing_from_actors = self.get_outgoing_from_actors(sub_transactions)
                    
        return {
            "incoming_total": incoming_total, 
            "outgoing_total": outgoing_total, 
            "balance": balance, 
            "outgoing_from_actors": outgoing_from_actors
        }
    
    def get_outgoing_from_actors(self, sub_transactions: list) -> dict:
        return sum([sub_transaction.amount for sub_transaction in sub_transactions if sub_transaction.actor])
