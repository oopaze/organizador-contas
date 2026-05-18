from urllib.parse import urlparse

from modules.ai.mcp.oauth.exceptions import InvalidRequestError


class RegisterClientUseCase:
    def __init__(self, client_repository, token_generator):
        self.client_repository = client_repository
        self.token_generator = token_generator

    def execute(self, *, name: str, redirect_uris: list[str]):
        if not redirect_uris:
            raise InvalidRequestError("redirect_uris required")
        for uri in redirect_uris:
            parsed = urlparse(uri)
            if parsed.scheme == "https":
                continue
            if parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1"):
                continue
            raise InvalidRequestError(f"redirect_uri {uri!r} must use https (http allowed only for localhost)")

        client_id = self.token_generator.generate_client_id()
        return self.client_repository.create(
            client_id=client_id, name=name or "Unnamed Client", redirect_uris=redirect_uris,
        )
