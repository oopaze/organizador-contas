"""
Unit tests for StartConversionUseCase.

These tests verify that the use case correctly starts conversations.
All external dependencies (AI services, repositories) are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.chat.use_cases.conversion.start import StartConversionUseCase
from modules.ai.chat.domains import ConversationDomain, MessageDomain
from modules.ai.domains.ai_response import AIResponseDomain


class TestStartConversionUseCase(SimpleTestCase):
    """Test StartConversionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ask_use_case = Mock()
        self.mock_create_embedding_use_case = Mock()
        self.mock_ai_call_repository = Mock()
        self.mock_conversation_repository = Mock()
        self.mock_conversation_factory = Mock()
        self.mock_conversation_serializer = Mock()
        self.mock_message_factory = Mock()
        self.mock_message_repository = Mock()
        self.mock_message_serializer = Mock()
        self.mock_tools = [{"name": "tool1"}]

        self.use_case = StartConversionUseCase(
            ask_use_case=self.mock_ask_use_case,
            create_embedding_use_case=self.mock_create_embedding_use_case,
            ai_call_repository=self.mock_ai_call_repository,
            conversation_repository=self.mock_conversation_repository,
            conversation_factory=self.mock_conversation_factory,
            conversation_serializer=self.mock_conversation_serializer,
            message_factory=self.mock_message_factory,
            message_repository=self.mock_message_repository,
            message_serializer=self.mock_message_serializer,
            tools=self.mock_tools,
        )

    def test_execute_raises_error_without_user_id(self):
        """Test that execute raises ValueError when user_id is missing."""
        # Arrange
        data = {"content": "Hello"}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.use_case.execute(data)
        
        self.assertIn("User id is required", str(context.exception))

    def test_execute_creates_conversation_and_messages(self):
        """Test that execute creates a conversation and exchanges messages."""
        # Arrange
        user_id = 1
        content = "Hello, how are you?"
        data = {"user": user_id, "content": content}
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = "conv_123"
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_ai_call.id = "ai_call_123"
        
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.content = content
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = False
        
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.content = "I'm doing well, thanks!"
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_factory.build.return_value = mock_conversation
        self.mock_conversation_repository.create.return_value = mock_conversation
        self.mock_conversation_repository.update.return_value = mock_conversation
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        
        self.mock_conversation_serializer.serialize.return_value = {"id": "conv_123"}
        self.mock_message_serializer.serialize.side_effect = [
            {"id": "msg_1", "content": content},
            {"id": "msg_2", "content": "I'm doing well, thanks!"},
        ]

        # Act
        result = self.use_case.execute(data)

        # Assert
        self.mock_conversation_factory.build.assert_called_once()
        self.mock_conversation_repository.create.assert_called_once()
        self.assertEqual(self.mock_ask_use_case.execute.call_count, 2)  # Once for title, once for message
        self.assertEqual(result["conversation"]["id"], "conv_123")
        self.assertEqual(result["user_message"]["content"], content)
        self.assertEqual(result["ai_message"]["content"], "I'm doing well, thanks!")

    def test_execute_with_custom_model(self):
        """Test that execute uses custom model when provided."""
        # Arrange
        user_id = 1
        content = "Test message"
        model = "custom-model"
        data = {"user": user_id, "content": content}
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = "conv_123"
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = False
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = False
        
        self.mock_conversation_factory.build.return_value = mock_conversation
        self.mock_conversation_repository.create.return_value = mock_conversation
        self.mock_conversation_repository.update.return_value = mock_conversation
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_conversation_serializer.serialize.return_value = {"id": "conv_123"}
        self.mock_message_serializer.serialize.side_effect = [{"id": "1"}, {"id": "2"}]

        # Act
        self.use_case.execute(data, model=model)

        # Assert
        # Verify that ask_use_case was called with the custom model
        call_args_list = self.mock_ask_use_case.execute.call_args_list
        for call_args in call_args_list:
            self.assertEqual(call_args[1]["model"], model)

    def test_execute_creates_embeddings_when_needed(self):
        """Test that execute creates embeddings for messages when needed."""
        # Arrange
        user_id = 1
        content = "Test message"
        data = {"user": user_id, "content": content}
        
        mock_conversation = Mock(spec=ConversationDomain)
        mock_conversation.id = "conv_123"
        mock_conversation.chat_session_key = "session_123"
        mock_conversation.user_id = user_id
        
        mock_ai_call = Mock(spec=AIResponseDomain)
        mock_user_message = Mock(spec=MessageDomain)
        mock_user_message.content = content
        mock_user_message.embedding_id = None
        mock_user_message.should_create_embedding.return_value = True
        mock_ai_message = Mock(spec=MessageDomain)
        mock_ai_message.content = "AI response"
        mock_ai_message.embedding_id = None
        mock_ai_message.should_create_embedding.return_value = True
        
        self.mock_conversation_factory.build.return_value = mock_conversation
        self.mock_conversation_repository.create.return_value = mock_conversation
        self.mock_conversation_repository.update.return_value = mock_conversation
        self.mock_ask_use_case.execute.return_value = "ai_call_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_message_factory.build.return_value = mock_user_message
        self.mock_message_factory.build_ai_message.return_value = mock_ai_message
        self.mock_message_repository.create.side_effect = [mock_user_message, mock_ai_message]
        self.mock_create_embedding_use_case.execute.return_value = "embedding_123"
        self.mock_conversation_serializer.serialize.return_value = {"id": "conv_123"}
        self.mock_message_serializer.serialize.side_effect = [{"id": "1"}, {"id": "2"}]

        # Act
        self.use_case.execute(data)

        # Assert
        # Should create embeddings for both user and AI messages
        self.assertEqual(self.mock_create_embedding_use_case.execute.call_count, 2)

