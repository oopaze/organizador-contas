from dependency_injector import containers, providers

from modules.ai.mcp.oauth.factories.client import OAuthClientFactory
from modules.ai.mcp.oauth.factories.auth_code import AuthorizationCodeFactory
from modules.ai.mcp.oauth.factories.access_token import AccessTokenFactory
from modules.ai.mcp.oauth.repositories.client import OAuthClientRepository
from modules.ai.mcp.oauth.repositories.auth_code import AuthorizationCodeRepository
from modules.ai.mcp.oauth.repositories.access_token import AccessTokenRepository
from modules.ai.mcp.oauth.services.pkce import PKCEService
from modules.ai.mcp.oauth.services.token_generator import TokenGeneratorService
from modules.ai.mcp.oauth.use_cases.register_client import RegisterClientUseCase
from modules.ai.mcp.oauth.use_cases.authorize import AuthorizeUseCase
from modules.ai.mcp.oauth.use_cases.exchange_code import ExchangeCodeUseCase
from modules.ai.mcp.oauth.use_cases.verify_token import VerifyTokenUseCase
from modules.ai.mcp.oauth.use_cases.revoke import RevokeUseCase
from modules.ai.mcp.oauth.use_cases.list_connections import ListConnectionsUseCase


class OAuthContainer(containers.DeclarativeContainer):
    # FACTORIES
    client_factory = providers.Singleton(OAuthClientFactory)
    auth_code_factory = providers.Singleton(AuthorizationCodeFactory)
    access_token_factory = providers.Singleton(AccessTokenFactory)

    # SERVICES
    pkce_service = providers.Singleton(PKCEService)
    token_generator = providers.Singleton(TokenGeneratorService)

    # REPOSITORIES
    client_repository = providers.Singleton(
        OAuthClientRepository, factory=client_factory,
    )
    auth_code_repository = providers.Singleton(
        AuthorizationCodeRepository, factory=auth_code_factory,
    )
    access_token_repository = providers.Singleton(
        AccessTokenRepository, factory=access_token_factory,
    )

    # USE CASES
    register_client_use_case = providers.Singleton(
        RegisterClientUseCase,
        client_repository=client_repository,
        token_generator=token_generator,
    )
    authorize_use_case = providers.Singleton(
        AuthorizeUseCase,
        client_repository=client_repository,
        auth_code_repository=auth_code_repository,
        token_generator=token_generator,
    )
    exchange_code_use_case = providers.Singleton(
        ExchangeCodeUseCase,
        auth_code_repository=auth_code_repository,
        access_token_repository=access_token_repository,
        token_generator=token_generator,
        pkce_service=pkce_service,
    )
    verify_token_use_case = providers.Singleton(
        VerifyTokenUseCase,
        access_token_repository=access_token_repository,
        token_generator=token_generator,
    )
    revoke_use_case = providers.Singleton(
        RevokeUseCase,
        access_token_repository=access_token_repository,
        token_generator=token_generator,
    )
    list_connections_use_case = providers.Singleton(
        ListConnectionsUseCase,
        client_repository=client_repository,
    )
