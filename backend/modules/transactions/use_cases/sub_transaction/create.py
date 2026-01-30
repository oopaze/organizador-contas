from modules.transactions.factories import SubTransactionFactory
from modules.transactions.repositories import SubTransactionRepository, TransactionRepository, ActorRepository
from modules.transactions.serializers import SubTransactionSerializer


class CreateSubTransactionUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        actor_repository: ActorRepository,
        sub_transaction_repository: SubTransactionRepository,
        sub_transaction_serializer: SubTransactionSerializer,
        sub_transaction_factory: SubTransactionFactory,
    ):
        self.transaction_repository = transaction_repository
        self.actor_repository = actor_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer
        self.sub_transaction_factory = sub_transaction_factory

    def execute(self, data: dict, user_id: int) -> dict:
        transaction = self.transaction_repository.get(data["transaction_id"], user_id)
        actor = self.actor_repository.get(data["actor"], user_id) if "actor" in data else None
        sub_transaction = self.sub_transaction_factory.build(data, transaction, actor)

        created_sub_transaction = self.sub_transaction_repository.create(sub_transaction)
        return self.sub_transaction_serializer.serialize(created_sub_transaction)
