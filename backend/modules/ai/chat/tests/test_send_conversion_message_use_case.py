"""
Unit tests for SendConversionMessageUseCase.

These tests verify that the use case correctly sends messages in conversations.
All external dependencies (AI services, repositories) are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.chat.use_cases.conversion.message.send import SendConversionMessageUseCase
from modules.ai.chat.domains import ConversationDomain, MessageDomain
from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.domains.embedding import EmbeddingDomain


class TestSendConversionMessageUseCase(SimpleTestCase):
    """Test SendConversionMessageUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ask_use_case = Mock()
        self.mock_create_embedding_use_case = Mock()
        self.mock_embedding_call_repository = Mock()
        self.mock_ai_call_repository = Mock()
        self.mock_conversation_repository = Mock()
        self.mock_message_repository = Mock()
        self.mock_message_factory = Mock()
        self.mock_message_serializer = Mock()
        self.mock_tools = [{"name": "tool1"}]

        self.use_case = SendConversionMessageUseCase(
            ask_use_case=self.mock_ask_use_case,
            create_embedding_use_case=self.mock_create_embedding_use_case,
            embedding_call_repository=self.mock_embedding_call_repository,
            ai_call_repository=self.mock_ai_call_repository,
            conversation_repository=self.mock_conversation_repository,
            message_repository=self.mock_message_repository,
            message_factory=self.mock_message_factory,
            message_serializer=self.mock_message_serializer,
            tools=self.mock_tools,
        )

    def test_execute_sends_message_and_gets_ai_response(self):
        """Test that execute sends a message and gets AI response."""
        # Arrange
        conversation_id = 1
        content = "What's the weather?"
        user_id = 1
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = conversation_id
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_ai_call.id = "ai_call_123"
        
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.content = content
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = False
        
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.content = "It's sunny today!"
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_repository.get.return_value = mock_conversation
        self.mock_message_repository.get_history_from_conversation.return_value = []
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_message_factory.build_from_model.return_value = Mock()
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_message_serializer.serialize.side_effect = [
            {"id": "msg_1", "content": content},
            {"id": "msg_2", "content": "It's sunny today!"},
        ]
        self.mock_message_serializer.serialize_many_for_history.return_value = ""

        # Act
        result = self.use_case.execute(conversation_id, content, user_id)

        # Assert
        self.mock_conversation_repository.get.assert_called_once_with(conversation_id, user_id)
        self.mock_ask_use_case.execute.assert_called_once()
        self.assertEqual(result["user_message"]["content"], content)
        self.assertEqual(result["ai_message"]["content"], "It's sunny today!")

    def test_execute_with_custom_model(self):
        """Test that execute uses custom model when provided."""
        # Arrange
        conversation_id = 1
        content = "Test message"
        user_id = 1
        model = "custom-model"
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = conversation_id
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = False
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_repository.get.return_value = mock_conversation
        self.mock_message_repository.get_history_from_conversation.return_value = []
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_message_serializer.serialize.side_effect = [{"id": "1"}, {"id": "2"}]
        self.mock_message_serializer.serialize_many_for_history.return_value = ""

        # Act
        self.use_case.execute(conversation_id, content, user_id, model=model)

        # Assert
        call_args = self.mock_ask_use_case.execute.call_args
        self.assertEqual(call_args[1]["model"], model)

    def test_execute_includes_conversation_history(self):
        """Test that execute includes conversation history in AI request."""
        # Arrange
        conversation_id = 1
        content = "Follow-up question"
        user_id = 1
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = conversation_id
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_history_message = Mock()
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = False
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_repository.get.return_value = mock_conversation
        self.mock_message_repository.get_history_from_conversation.return_value = [mock_history_message]
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_message_factory.build_from_model.return_value = Mock(spec=MessageDomain)
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_message_serializer.serialize.side_effect = [{"id": "1"}, {"id": "2"}]
        self.mock_message_serializer.serialize_many_for_history.return_value = "Previous conversation..."

        # Act
        self.use_case.execute(conversation_id, content, user_id)

        # Assert
        self.mock_message_repository.get_history_from_conversation.assert_called_once_with(
            conversation_id, limit=10
        )
        call_args = self.mock_ask_use_case.execute.call_args
        self.assertEqual(call_args[1]["history"], "Previous conversation...")

    def test_execute_uses_contextualized_messages_with_embedding(self):
        """Test that execute uses contextualized messages when embedding is available."""
        # Arrange
        conversation_id = 1
        content = "Question with context"
        user_id = 1
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = conversation_id
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_embedding = Mock(spec=EmbeddingDomain)
        mock_embedding.embedding = [0.1, 0.2, 0.3]
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.content = content
        mock_user_message.embedding_id = "embedding_123"
        mock_user_message.should_create_embedding.return_value = True
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.content = "AI response"
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_repository.get.return_value = mock_conversation
        self.mock_message_repository.get_history_from_conversation.return_value = []
        self.mock_message_repository.get_contextualized_messages_from_conversation.return_value = []
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_create_embedding_use_case.execute.return_value = "embedding_123"
        self.mock_embedding_call_repository.get.return_value = mock_embedding
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_message_serializer.serialize.side_effect = [{"id": "1"}, {"id": "2"}]
        self.mock_message_serializer.serialize_many_for_history.return_value = ""

        # Act
        self.use_case.execute(conversation_id, content, user_id)

        # Assert
        self.mock_embedding_call_repository.get.assert_called_once_with("embedding_123")
        self.mock_message_repository.get_contextualized_messages_from_conversation.assert_called_once()

