class RevokeUseCase:
    def __init__(self, access_token_repository, token_generator):
        self.access_token_repository = access_token_repository
        self.token_generator = token_generator

    def execute_by_token(self, *, plaintext_token: str) -> int:
        token_hash = self.token_generator.hash_token(plaintext_token)
        return self.access_token_repository.revoke_by_hash(token_hash)

    def execute_by_client(self, *, client_id: str, user_id: int) -> int:
        return self.access_token_repository.revoke_all(
            client_id=client_id, user_id=user_id,
        )
