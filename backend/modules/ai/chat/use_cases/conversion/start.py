from typing import TypedDict

from modules.ai.types import LlmModels
from modules.ai.prompts import (
    SCOPE_BOUNDARIES_PROMPT, 
    ASK_TITLE_FROM_MESSAGE_PROMPT, 
    ASK_USER_MESSAGE_PROMPT, 
    MODELS_EXPLANATION_PROMPT,
    BOT_DESCRIPTION,
)
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.use_cases.create_embedding import CreateEmbeddingUseCase
from modules.ai.chat.repositories import ConversationRepository, MessageRepository, AICallRepository
from modules.ai.chat.factories import ConversationFactory, MessageFactory
from modules.ai.chat.domains import ConversationDomain, MessageDomain
from modules.ai.chat.serializers import ConversationSerializer, MessageSerializer
from modules.ai.gateways.openai_embedding import EmbeddingModels


class StartConversionData(TypedDict):
    user: int
    content: str


class StartConversionUseCase:
    embedding_model = EmbeddingModels.TEXT_EMBEDDING_3_SMALL
    
    def __init__(
        self,
        ask_use_case: AskUseCase,
        create_embedding_use_case: CreateEmbeddingUseCase,
        ai_call_repository: AICallRepository,
        conversation_repository: ConversationRepository,
        conversation_factory: ConversationFactory,
        conversation_serializer: ConversationSerializer,
        message_factory: MessageFactory,
        message_repository: MessageRepository,
        message_serializer: MessageSerializer,
        tools: list[dict],
    ):
        self.ask_use_case = ask_use_case
        self.create_embedding_use_case = create_embedding_use_case

        self.ai_call_repository = ai_call_repository
        self.conversation_repository = conversation_repository
        self.conversation_factory = conversation_factory
        self.conversation_serializer = conversation_serializer

        self.message_factory = message_factory
        self.message_repository = message_repository
        self.message_serializer = message_serializer
        self.tools = tools

    def execute(self, data: StartConversionData, model: str = LlmModels.DEEPSEEK_CHAT.name) -> dict:
        user_id = data.get("user")
        
        if not user_id:
            raise ValueError("User id is required")
        
        content = data.get("content", "")

        conversation = self._generate_conversion(user_id, content, model=model)
        user_message, ai_message = self._forward_user_message_to_ai(conversation, content, model=model)

        return {
            "conversation":  self.conversation_serializer.serialize(conversation),
            "user_message": self.message_serializer.serialize(user_message),
            "ai_message": self.message_serializer.serialize(ai_message),
        }
    
    def _generate_conversion(self, user_id: int, content: str, model: str = LlmModels.DEEPSEEK_CHAT.name) -> dict:
        conversation = self.conversation_factory.build()
        conversation = self.conversation_repository.create(conversation, user_id)

        prompts_for_title = [SCOPE_BOUNDARIES_PROMPT, MODELS_EXPLANATION_PROMPT, BOT_DESCRIPTION, ASK_TITLE_FROM_MESSAGE_PROMPT.format(content=content)]

        ai_call_id = self.ask_use_case.execute(
            prompts_for_title, 
            model=model,
            tools=self.tools, 
            chat_session_key=conversation.chat_session_key,
            user_id=user_id,
        )
        ai_call = self.ai_call_repository.get(ai_call_id)
        conversation.update_ai_call(ai_call)

        return self.conversation_repository.update(
            conversation, 
            user_id,
        )
    
    def _forward_user_message_to_ai(
        self, 
        conversation: ConversationDomain, 
        content: str, 
        model: str = LlmModels.GOOGLE_GEMINI_2_5_FLASH_LITE.name
    ) -> MessageDomain:
        user_message = self.message_factory.build(content, conversation.id)

        prompts_for_user_message = [SCOPE_BOUNDARIES_PROMPT, MODELS_EXPLANATION_PROMPT, BOT_DESCRIPTION, ASK_USER_MESSAGE_PROMPT.format(content=content)]
        ai_call_id = self.ask_use_case.execute(
            prompts_for_user_message, 
            model=model, 
            tools=self.tools, 
            chat_session_key=conversation.chat_session_key,
            user_id=conversation.user_id,
        )
        ai_call = self.ai_call_repository.get(ai_call_id)

        user_message.update_ai_call(ai_call)
        user_message.update_embedding_id(self._create_embedding_for_message(user_message))
        user_message = self.message_repository.create(user_message)

        ai_message = self.message_factory.build_ai_message(ai_call, conversation.id, user_message)
        ai_message.update_embedding_id(self._create_embedding_for_message(ai_message))
        ai_message = self.message_repository.create(ai_message)

        return user_message, ai_message
    
    def _create_embedding_for_message(self, message: MessageDomain) -> int:
        if message.should_create_embedding():
            embedding_id = self.create_embedding_use_case.execute(message.content, model=self.embedding_model)
            message.update_embedding_id(embedding_id)
        return message.embedding_id
