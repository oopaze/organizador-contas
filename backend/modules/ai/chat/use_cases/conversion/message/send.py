from modules.ai.types import LlmModels
from modules.ai.prompts import SCOPE_BOUNDARIES_PROMPT, ASK_USER_MESSAGE_PROMPT, MODELS_EXPLANATION_PROMPT, BOT_DESCRIPTION
from modules.ai.chat.factories import MessageFactory
from modules.ai.chat.repositories import AICallRepository, MessageRepository, ConversationRepository, EmbeddingCallRepository
from modules.ai.chat.serializers import MessageSerializer
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.use_cases.create_embedding import CreateEmbeddingUseCase
from modules.ai.gateways.openai_embedding import EmbeddingModels
from modules.ai.chat.domains import MessageDomain, ConversationDomain


class SendConversionMessageUseCase:
    embedding_model = EmbeddingModels.TEXT_EMBEDDING_3_SMALL

    def __init__(
        self,
        ask_use_case: AskUseCase,
        create_embedding_use_case: CreateEmbeddingUseCase,
        embedding_call_repository: EmbeddingCallRepository,
        ai_call_repository: AICallRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        message_factory: MessageFactory,
        message_serializer: MessageSerializer,
        tools: list[dict],
    ):
        self.ask_use_case = ask_use_case
        self.create_embedding_use_case = create_embedding_use_case
        self.embedding_call_repository = embedding_call_repository
        self.ai_call_repository = ai_call_repository
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.message_factory = message_factory
        self.message_serializer = message_serializer
        self.tools = tools

    def execute(self, conversation_id: int, content: str, user_id: int, model: str = LlmModels.DEEPSEEK_CHAT.name) -> dict:
        conversation = self.conversation_repository.get(conversation_id, user_id)
        return self._forward_user_message_to_ai(conversation, content, model=model)
    
    def _forward_user_message_to_ai(
            self, 
            conversation: ConversationDomain, 
            content: str, 
            model: str = LlmModels.DEEPSEEK_CHAT.name
        ) -> MessageDomain:
        user_message = self.message_factory.build(content, conversation.id)
        user_message.update_embedding_id(self._create_embedding_for_message(user_message))

        prompts_for_user_message = [SCOPE_BOUNDARIES_PROMPT, MODELS_EXPLANATION_PROMPT, BOT_DESCRIPTION, ASK_USER_MESSAGE_PROMPT.format(content=content)]
        history = self._get_history_from_conversation(conversation.id, user_message.embedding_id)
        history_as_string = self.message_serializer.serialize_many_for_history(history)
        ai_call_id = self.ask_use_case.execute(
            prompts_for_user_message, 
            model=model, 
            tools=self.tools, 
            chat_session_key=conversation.chat_session_key,
            history=history_as_string
        )
        ai_call = self.ai_call_repository.get(ai_call_id)

        user_message.update_ai_call(ai_call)
        user_message = self.message_repository.create(user_message)

        ai_message = self.message_factory.build_ai_message(ai_call, conversation.id, user_message)
        ai_message.update_embedding_id(self._create_embedding_for_message(ai_message))
        ai_message = self.message_repository.create(ai_message)

        return {
            "user_message": self.message_serializer.serialize(user_message),
            "ai_message": self.message_serializer.serialize(ai_message),
        }
    
    def _get_history_from_conversation(self, conversation_id: int, embedding_id: int) -> list[MessageDomain]:
        history = self.message_repository.get_history_from_conversation(conversation_id, limit=10)
        if embedding_id:
            embedding = self.embedding_call_repository.get(embedding_id)
            history = self.message_repository.get_contextualized_messages_from_conversation(embedding.embedding, conversation_id)
        return [self.message_factory.build_from_model(message) for message in history]
    
    def _create_embedding_for_message(self, message: MessageDomain) -> int:
        if message.should_create_embedding():
            embedding_id = self.create_embedding_use_case.execute(message.content, model=self.embedding_model)
            message.update_embedding_id(embedding_id)
        return message.embedding_id
