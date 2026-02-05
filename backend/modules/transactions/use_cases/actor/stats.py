from modules.transactions.repositories import ActorRepository, SubTransactionRepository
from modules.transactions.domains import ActorDomain


class ActorStatsUseCase:
    def __init__(self, actor_repository: ActorRepository, sub_transaction_repository: SubTransactionRepository):
        self.actor_repository = actor_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, user_id: int, due_date: str = None, due_date_start: str = None, due_date_end: str = None) -> dict:
        filters = {
            "transaction__user_id": user_id
        }

        if due_date:
            filters["transaction__due_date__month"] = due_date.split("-")[1]
            filters["transaction__due_date__year"] = due_date.split("-")[0]

        elif due_date_start and due_date_end:
            filters["transaction__due_date__gte"] = due_date_start
            filters["transaction__due_date__lte"] = due_date_end

        actors = self.actor_repository.get_all(user_id)
        sub_transactions = self.sub_transaction_repository.filter_by_actor_ids([actor.id for actor in actors], filters)

        actors_with_sub_transactions = []
        for actor in actors:
            actor_sub_transactions = [sub_transaction for sub_transaction in sub_transactions if sub_transaction.actor.id == actor.id]
            if actor_sub_transactions:
                actor.set_sub_transactions([sub_transaction for sub_transaction in sub_transactions if sub_transaction.actor.id == actor.id])
                actors_with_sub_transactions.append(actor)

        return self.calculate_stats(actors_with_sub_transactions)
    
    def calculate_stats(self, actors: list[ActorDomain]) -> dict:
        total_spent = sum([actor.get_total_spent() for actor in actors]) if actors else None
        biggest_spender = max(actors, key=lambda actor: actor.get_total_spent()) if actors else None
        smallest_spender = min(actors, key=lambda actor: actor.get_total_spent()) if actors else None

        return {
            "total_spent": total_spent,
            "total_spent_paid": sum([actor.get_total_spent_paid() for actor in actors]) if actors else None,
            "biggest_spender": biggest_spender.name if biggest_spender else None,
            "biggest_spender_amount": biggest_spender.get_total_spent() if biggest_spender else None,
            "smallest_spender": smallest_spender.name if smallest_spender else None,
            "smallest_spender_amount": smallest_spender.get_total_spent() if smallest_spender else None,
            "average_spent": total_spent / len(actors) if actors else None,
            "active_actors": len([actor for actor in actors if actor.get_total_spent() > 0]) if actors else None
        }
