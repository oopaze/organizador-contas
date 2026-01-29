from typing import TypedDict

from modules.ai.prompts import SCOPE_BOUNDARIES_PROMPT, ASK_TITLE_FROM_MESSAGE_PROMPT, ASK_USER_MESSAGE_PROMPT
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.chat.repositories import ConversationRepository, MessageRepository, AICallRepository
from modules.ai.chat.factories import ConversationFactory, MessageFactory
from modules.ai.chat.models import Message
from modules.ai.chat.serializers import ConversationSerializer, MessageSerializer


class StartConversionData(TypedDict):
    user: int
    content: str


class StartConversionUseCase:
    def __init__(
        self,
        ask_use_case: AskUseCase,
        ai_call_repository: AICallRepository,
        conversation_repository: ConversationRepository,
        conversation_factory: ConversationFactory,
        conversation_serializer: ConversationSerializer,
        message_factory: MessageFactory,
        message_repository: MessageRepository,
        message_serializer: MessageSerializer,
    ):
        self.ask_use_case = ask_use_case
        self.ai_call_repository = ai_call_repository
        self.conversation_repository = conversation_repository
        self.conversation_factory = conversation_factory
        self.conversation_serializer = conversation_serializer

        self.message_factory = message_factory
        self.message_repository = message_repository
        self.message_serializer = message_serializer

    def execute(self, data: StartConversionData) -> dict:
        content = data["content"]

        prompts_for_title = [SCOPE_BOUNDARIES_PROMPT, ASK_TITLE_FROM_MESSAGE_PROMPT.format(content=content)]

        ai_call_id = self.ask_use_case.execute(prompts_for_title)
        ai_call = self.ai_call_repository.get(ai_call_id)

        conversation = self.conversation_repository.create(
            self.conversation_factory.build_from_ai_call(ai_call), 
            data["user"],
        )

        user_message = self.message_factory.build(content, conversation.id)

        prompts_for_user_message = [SCOPE_BOUNDARIES_PROMPT, ASK_USER_MESSAGE_PROMPT.format(content=content)]
        ai_call_id = self.ask_use_case.execute(prompts_for_user_message)
        ai_call = self.ai_call_repository.get(ai_call_id)

        user_message.update_ai_call(ai_call)
        user_message = self.message_repository.create(user_message)

        ai_message = self.message_factory.build(ai_call.response["text"], conversation.id, Message.Role.ASSISTANT)
        ai_message.update_ai_call(ai_call)
        ai_message = self.message_repository.create(ai_message)

        return {
            "conversation":  self.conversation_serializer.serialize(conversation),
            "user_message": self.message_serializer.serialize(user_message),
            "ai_message": self.message_serializer.serialize(ai_message),
        }
