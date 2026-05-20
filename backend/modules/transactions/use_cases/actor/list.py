from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer
from modules.transactions.repositories.sub_transaction import SubTransactionRepository
from modules.transactions.serializers.sub_transaction import SubTransactionSerializer
from modules.transactions.domains.actor import ActorDomain


class ListActorsUseCase:
    def __init__(
        self,
        actor_repository: ActorRepository,
        actor_serializer: ActorSerializer,
        sub_transaction_repository: SubTransactionRepository,
        sub_transaction_serializer: SubTransactionSerializer,
        loan_repository=None,
    ):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer
        self.loan_repository = loan_repository

    def execute(self, user_id: int, due_date: str = None, without_sub_transactions: bool = False) -> list[dict]:
        actors = self.actor_repository.get_all(user_id)
        if without_sub_transactions:
            return self.actor_serializer.serialize_many(actors)

        sub_transactions = self.sub_transaction_repository.get_all(user_id, due_date)
        separed_sub_transactions = self.separe_sub_transactions_by_actor(sub_transactions)

        loans_by_actor = self._fetch_loans_by_actor(user_id)

        return [
            self.get_actor_data(
                actor,
                separed_sub_transactions.get(actor.id, []),
                loans_by_actor.get(actor.id, []),
            )
            for actor in actors
        ]

    def _fetch_loans_by_actor(self, user_id: int) -> dict:
        if not self.loan_repository:
            return {}
        loans = self.loan_repository.get_all(user_id)
        grouped: dict = {}
        for loan in loans:
            grouped.setdefault(loan.actor_id, []).append(loan)
        return grouped

    def separe_sub_transactions_by_actor(self, sub_transactions: list["SubTransactionDomain"]) -> dict[int, list["SubTransactionDomain"]]:
        separed_sub_transactions = {}
        for sub_transaction in sub_transactions:
            if not sub_transaction.actor:
                continue

            if sub_transaction.actor.id in separed_sub_transactions:
                separed_sub_transactions[sub_transaction.actor.id].append(sub_transaction)
            else:
                separed_sub_transactions[sub_transaction.actor.id] = [sub_transaction]
        return separed_sub_transactions

    def get_actor_data(
        self,
        actor: ActorDomain,
        sub_transactions: list["SubTransactionDomain"],
        loans: list = None,
    ) -> dict:
        actor.set_sub_transactions(sub_transactions)
        actor.set_loans(loans or [])
        actor_data = self.actor_serializer.serialize(actor)
        return actor_data
