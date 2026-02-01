from dependency_injector import containers, providers
from django.conf import settings

from modules.ai.factories.ai_request import AIRequestFactory
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.factories.embedding import EmbeddingFactory
from modules.ai.gateways import OpenAIEmbeddingGateway, LLMGateway
from modules.ai.models import AICall, EmbeddingCall
from modules.ai.repositories import AICallRepository, EmbeddingRepository
from modules.ai.services.llm import LLMService
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.use_cases.create_embedding import CreateEmbeddingUseCase


class AIContainer(containers.DeclarativeContainer):
    # FACTORIES
    ai_request_factory = providers.Factory(AIRequestFactory)
    ai_response_factory = providers.Factory(AIResponseFactory)
    embedding_factory = providers.Factory(EmbeddingFactory)

    # GATEWAYS
    deepseek_llm_gateway = providers.Factory(
        LLMGateway,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        ai_request_factory=ai_request_factory,
    )
    google_llm_gateway = providers.Factory(
        LLMGateway,
        api_key=settings.GOOGLE_AI_API_KEY,
        base_url=settings.GOOGLE_AI_BASE_URL,
        ai_request_factory=ai_request_factory,
    )
    openai_llm_gateway = providers.Factory(
        LLMGateway,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        ai_request_factory=ai_request_factory,
    )
    openai_embedding_gateway = providers.Factory(OpenAIEmbeddingGateway, api_key=settings.OPENAI_API_KEY)

    # SERVICES
    llm_service = providers.Factory(
        LLMService,
        deepseek_llm_gateway=deepseek_llm_gateway,
        google_llm_gateway=google_llm_gateway,
        openai_llm_gateway=openai_llm_gateway,
    )

    # REPOSITORIES
    ai_call_repository = providers.Factory(AICallRepository, model=AICall, ai_response_factory=ai_response_factory)
    embedding_repository = providers.Factory(EmbeddingRepository, model=EmbeddingCall, embedding_factory=embedding_factory)

    # USE CASES
    ask_use_case = providers.Factory(
        AskUseCase,
        ai_request_factory=ai_request_factory,
        ai_response_factory=ai_response_factory,
        llm_service=llm_service,
        ai_call_repository=ai_call_repository,
    )

    create_embedding_use_case = providers.Factory(
        CreateEmbeddingUseCase,
        openai_embedding_gateway=openai_embedding_gateway,
        embedding_repository=embedding_repository,
        embedding_factory=embedding_factory,
    )
