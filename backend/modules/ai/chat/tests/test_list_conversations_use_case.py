"""
Unit tests for ListConversationsUseCase.

These tests verify that the use case correctly lists conversations.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.chat.use_cases.conversion.list import ListConversationsUseCase
from modules.ai.chat.domains import ConversationDomain


class TestListConversationsUseCase(SimpleTestCase):
    """Test ListConversationsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conversation_repository = Mock()
        self.mock_conversation_serializer = Mock()

        self.use_case = ListConversationsUseCase(
            conversation_repository=self.mock_conversation_repository,
            conversation_serializer=self.mock_conversation_serializer,
        )

    def test_execute_returns_serialized_conversations(self):
        """Test that execute returns a list of serialized conversations."""
        # Arrange
        user_id = 1
        mock_conversation1 = Mock(spec=ConversationDomain)
        mock_conversation2 = Mock(spec=ConversationDomain)
        
        self.mock_conversation_repository.get_all_by_user_id.return_value = [
            mock_conversation1, mock_conversation2
        ]
        self.mock_conversation_serializer.serialize.side_effect = [
            {"id": "1", "title": "Conversation 1"},
            {"id": "2", "title": "Conversation 2"},
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_conversation_repository.get_all_by_user_id.assert_called_once_with(user_id)
        self.assertEqual(self.mock_conversation_serializer.serialize.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["id"], "2")

    def test_execute_with_empty_results(self):
        """Test that execute handles empty conversation list."""
        # Arrange
        user_id = 1
        self.mock_conversation_repository.get_all_by_user_id.return_value = []

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_conversation_repository.get_all_by_user_id.assert_called_once_with(user_id)
        self.mock_conversation_serializer.serialize.assert_not_called()
        self.assertEqual(result, [])

    def test_execute_serializes_all_conversations(self):
        """Test that execute serializes all conversations from repository."""
        # Arrange
        user_id = 1
        mock_conversations = [Mock(spec=ConversationDomain) for _ in range(3)]
        
        self.mock_conversation_repository.get_all_by_user_id.return_value = mock_conversations
        self.mock_conversation_serializer.serialize.side_effect = [
            {"id": str(i), "title": f"Conv {i}"} for i in range(3)
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(self.mock_conversation_serializer.serialize.call_count, 3)
        self.assertEqual(len(result), 3)
        for i, conv_data in enumerate(result):
            self.assertEqual(conv_data["id"], str(i))
            self.assertEqual(conv_data["title"], f"Conv {i}")

