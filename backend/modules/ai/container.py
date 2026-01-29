from dependency_injector import containers, providers
from django.conf import settings

from modules.ai.factories.ai_request import AIRequestFactory
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.gateways.gemini import GoogleLLMGateway
from modules.ai.models import AICall
from modules.ai.repositories import AICallRepository
from modules.ai.use_cases.ask import AskUseCase


class AIContainer(containers.DeclarativeContainer):
    # FACTORIES
    ai_request_factory = providers.Factory(AIRequestFactory)
    ai_response_factory = providers.Factory(AIResponseFactory)

    # GATEWAYS
    google_llm_gateway = providers.Factory(GoogleLLMGateway, api_key=settings.GOOGLE_AI_API_KEY)

    # REPOSITORIES
    ai_call_repository = providers.Factory(AICallRepository, model=AICall, ai_response_factory=ai_response_factory)

    # USE CASES
    ask_use_case = providers.Factory(
        AskUseCase,
        ai_request_factory=ai_request_factory,
        ai_response_factory=ai_response_factory,
        google_llm_gateway=google_llm_gateway,
        ai_call_repository=ai_call_repository,
    )
