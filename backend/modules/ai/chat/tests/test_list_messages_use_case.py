"""
Unit tests for ListMessagesUseCase.

These tests verify that the use case correctly lists messages.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.chat.use_cases.conversion.message.list import ListMessagesUseCase
from modules.ai.chat.domains import MessageDomain


class TestListMessagesUseCase(SimpleTestCase):
    """Test ListMessagesUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_message_repository = Mock()
        self.mock_message_serializer = Mock()

        self.use_case = ListMessagesUseCase(
            message_repository=self.mock_message_repository,
            message_serializer=self.mock_message_serializer,
        )

    def test_execute_returns_serialized_messages(self):
        """Test that execute returns a list of serialized messages."""
        # Arrange
        conversation_id = 1
        user_id = 1
        mock_message1 = Mock(spec=MessageDomain)
        mock_message2 = Mock(spec=MessageDomain)
        
        self.mock_message_repository.get_all_by_conversation_id.return_value = [
            mock_message1, mock_message2
        ]
        self.mock_message_serializer.serialize.side_effect = [
            {"id": "1", "content": "Hello"},
            {"id": "2", "content": "Hi there"},
        ]

        # Act
        result = self.use_case.execute(conversation_id, user_id)

        # Assert
        self.mock_message_repository.get_all_by_conversation_id.assert_called_once_with(
            conversation_id, user_id
        )
        self.assertEqual(self.mock_message_serializer.serialize.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"], "Hello")
        self.assertEqual(result[1]["content"], "Hi there")

    def test_execute_with_empty_results(self):
        """Test that execute handles empty message list."""
        # Arrange
        conversation_id = 1
        user_id = 1
        self.mock_message_repository.get_all_by_conversation_id.return_value = []

        # Act
        result = self.use_case.execute(conversation_id, user_id)

        # Assert
        self.mock_message_repository.get_all_by_conversation_id.assert_called_once()
        self.mock_message_serializer.serialize.assert_not_called()
        self.assertEqual(result, [])

    def test_execute_passes_correct_parameters(self):
        """Test that execute passes correct parameters to repository."""
        # Arrange
        conversation_id = 123
        user_id = 456
        self.mock_message_repository.get_all_by_conversation_id.return_value = []

        # Act
        self.use_case.execute(conversation_id, user_id)

        # Assert
        self.mock_message_repository.get_all_by_conversation_id.assert_called_once_with(
            conversation_id, user_id
        )

    def test_execute_serializes_all_messages(self):
        """Test that execute serializes all messages from repository."""
        # Arrange
        conversation_id = 1
        user_id = 1
        mock_messages = [Mock(spec=MessageDomain) for _ in range(5)]
        
        self.mock_message_repository.get_all_by_conversation_id.return_value = mock_messages
        self.mock_message_serializer.serialize.side_effect = [
            {"id": str(i), "content": f"Message {i}"} for i in range(5)
        ]

        # Act
        result = self.use_case.execute(conversation_id, user_id)

        # Assert
        self.assertEqual(self.mock_message_serializer.serialize.call_count, 5)
        self.assertEqual(len(result), 5)
        for i, msg_data in enumerate(result):
            self.assertEqual(msg_data["id"], str(i))
            self.assertEqual(msg_data["content"], f"Message {i}")

