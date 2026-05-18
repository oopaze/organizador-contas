class ListConnectionsUseCase:
    def __init__(self, client_repository):
        self.client_repository = client_repository

    def execute(self, *, user_id: int) -> list[dict]:
        clients = self.client_repository.list_for_user(user_id=user_id)
        return [
            {"client_id": c.client_id, "name": c.name}
            for c in clients
        ]
