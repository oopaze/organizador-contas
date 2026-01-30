from modules.ai.prompts import SCOPE_BOUNDARIES_PROMPT, ASK_USER_MESSAGE_PROMPT, MODELS_EXPLANATION_PROMPT
from modules.ai.chat.factories import MessageFactory
from modules.ai.chat.repositories import AICallRepository, MessageRepository, ConversationRepository, EmbeddingCallRepository
from modules.ai.chat.serializers import MessageSerializer
from modules.ai.chat.models import Message
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.use_cases.create_embedding import CreateEmbeddingUseCase
from modules.ai.gateways.gemini import GoogleModels
from modules.ai.gateways.openai_embedding import EmbeddingModels
from google.genai.types import ToolListUnion


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
        tools: list[ToolListUnion],
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

    def execute(self, conversation_id: int, content: str, user_id: int, model: str = GoogleModels.GEMINI_2_5_FLASH_LITE) -> dict:
        conversation = self.conversation_repository.get(conversation_id, user_id)

        user_message = self.message_factory.build(content, conversation_id)
        history = []
        if user_message.should_create_embedding():
            embedding_id = self.create_embedding_use_case.execute(user_message.content, model=self.embedding_model)
            user_message.update_embedding_id(embedding_id)

            embedding = self.embedding_call_repository.get(embedding_id)
            contextualized_history = self.message_repository.get_contextualized_messages_from_conversation(embedding.embedding, conversation.id)
            history.extend([self.message_serializer.serialize_only_content_and_role(message) for message in contextualized_history])
 
        prompts_for_user_message = [SCOPE_BOUNDARIES_PROMPT, MODELS_EXPLANATION_PROMPT, ASK_USER_MESSAGE_PROMPT.format(content=content)]

        ai_call_id = self.ask_use_case.execute(prompts_for_user_message, model=model, history=history, tools=self.tools)
        ai_call = self.ai_call_repository.get(ai_call_id)

        user_message.update_ai_call(ai_call)
        user_message = self.message_repository.create(user_message)

        ai_message = self.message_factory.build(ai_call.response["text"], conversation_id, Message.Role.ASSISTANT)
        ai_message.update_ai_call(ai_call)
        if ai_message.should_create_embedding():
            embedding_id = self.create_embedding_use_case.execute(ai_message.content, model=self.embedding_model)
            ai_message.update_embedding_id(embedding_id)
        
        ai_message = self.message_repository.create(ai_message)
        
        return {
            "user_message": self.message_serializer.serialize(user_message),
            "ai_message": self.message_serializer.serialize(ai_message),
        }
