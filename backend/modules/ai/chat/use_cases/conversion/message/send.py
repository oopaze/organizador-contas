from modules.ai.prompts import SCOPE_BOUNDARIES_PROMPT, ASK_USER_MESSAGE_PROMPT
from modules.ai.chat.factories import MessageFactory
from modules.ai.chat.repositories import AICallRepository, MessageRepository, ConversationRepository
from modules.ai.chat.serializers import MessageSerializer
from modules.ai.chat.models import Message
from modules.ai.use_cases.ask import AskUseCase


class SendConversionMessageUseCase:
    def __init__(
        self,
        ask_use_case: AskUseCase,
        ai_call_repository: AICallRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        message_factory: MessageFactory,
        message_serializer: MessageSerializer,
    ):
        self.ask_use_case = ask_use_case
        self.ai_call_repository = ai_call_repository
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.message_factory = message_factory
        self.message_serializer = message_serializer

    def execute(self, conversation_id: int, content: str, user_id: int) -> dict:
        self.conversation_repository.get(conversation_id, user_id)

        user_message = self.message_factory.build(content, conversation_id)
        prompts_for_user_message = [SCOPE_BOUNDARIES_PROMPT, ASK_USER_MESSAGE_PROMPT.format(content=content)]

        ai_call_id = self.ask_use_case.execute(prompts_for_user_message)
        ai_call = self.ai_call_repository.get(ai_call_id)

        user_message.update_ai_call(ai_call)
        user_message = self.message_repository.create(user_message)

        ai_message = self.message_factory.build(ai_call.response["text"], conversation_id, Message.Role.ASSISTANT)
        ai_message.update_ai_call(ai_call)
        ai_message = self.message_repository.create(ai_message)

        return {
            "user_message": self.message_serializer.serialize(user_message),
            "ai_message": self.message_serializer.serialize(ai_message),
        }
