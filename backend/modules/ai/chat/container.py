from dependency_injector import containers, providers

from modules.ai.chat.factories import ConversationFactory, MessageFactory, AICallFactory
from modules.ai.chat.models import Conversation, Message
from modules.ai.models import AICall
from modules.ai.chat.repositories import ConversationRepository, MessageRepository, AICallRepository
from modules.ai.chat.serializers import ConversationSerializer, MessageSerializer, AICallSerializer
from modules.ai.chat.use_cases.conversion import StartConversionUseCase, ListConversationsUseCase
from modules.ai.chat.use_cases.conversion.message import ListMessagesUseCase, SendConversionMessageUseCase


class AIChatContainer(containers.DeclarativeContainer):
    # GATEWAYS
    ask_use_case = providers.Dependency()

    # FACTORIES
    ai_call_factory = providers.Factory(AICallFactory)
    conversation_factory = providers.Factory(ConversationFactory)
    message_factory = providers.Factory(MessageFactory, ai_call_factory=ai_call_factory)

    # REPOSITORIES
    ai_call_repository = providers.Factory(AICallRepository, model=AICall, ai_call_factory=ai_call_factory)
    conversation_repository = providers.Factory(ConversationRepository, model=Conversation, conversation_factory=conversation_factory)
    message_repository = providers.Factory(MessageRepository, model=Message, message_factory=message_factory)

    # SERIALIZERS
    ai_call_serializer = providers.Factory(AICallSerializer)
    message_serializer = providers.Factory(MessageSerializer, ai_call_serializer=ai_call_serializer)
    conversation_serializer = providers.Factory(ConversationSerializer, message_serializer=message_serializer)

    # USE CASES
    list_conversations_use_case = providers.Factory(
        ListConversationsUseCase,
        conversation_repository=conversation_repository,
        conversation_serializer=conversation_serializer,
    )

    list_messages_use_case = providers.Factory(
        ListMessagesUseCase,
        message_repository=message_repository,
        message_serializer=message_serializer,
    )

    send_conversion_message_use_case = providers.Factory(
        SendConversionMessageUseCase,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        message_factory=message_factory,
        message_serializer=message_serializer,
    )

    start_conversion_use_case = providers.Factory(
        StartConversionUseCase,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
        conversation_repository=conversation_repository,
        conversation_factory=conversation_factory,
        conversation_serializer=conversation_serializer,
        message_factory=message_factory,
        message_repository=message_repository,
        message_serializer=message_serializer,
    )
