"""
Unit tests for AskUseCase.

These tests verify that the use case correctly handles AI requests and responses.
All external dependencies (LLM service, repositories) are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.use_cases.ask import AskUseCase
from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.exceptions import LLMGatewayException


class TestAskUseCase(SimpleTestCase):
    """Test AskUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_request_factory = Mock()
        self.mock_ai_response_factory = Mock()
        self.mock_ai_call_repository = Mock()
        self.mock_llm_service = Mock()

        self.use_case = AskUseCase(
            ai_request_factory=self.mock_ai_request_factory,
            ai_response_factory=self.mock_ai_response_factory,
            ai_call_repository=self.mock_ai_call_repository,
            llm_service=self.mock_llm_service,
        )

    def test_execute_creates_ai_request_and_calls_llm(self):
        """Test that execute creates an AI request and calls the LLM service."""
        # Arrange
        prompt = ["What is the weather?"]
        user_id = 1
        model = "test-model"
        
        mock_ai_request = Mock(spec=AIRequestDomain)
        mock_llm_response = Mock()
        mock_ai_response = Mock(spec=AIResponseDomain)
        mock_saved_response = Mock(spec=AIResponseDomain)
        mock_saved_response.id = "response_123"
        
        self.mock_ai_request_factory.build.return_value = mock_ai_request
        self.mock_llm_service.ask.return_value = mock_llm_response
        self.mock_ai_response_factory.build_from_llm_response.return_value = mock_ai_response
        self.mock_ai_call_repository.create.return_value = mock_saved_response

        # Act
        result = self.use_case.execute(prompt, user_id, model=model)

        # Assert
        self.mock_ai_request_factory.build.assert_called_once_with(
            prompt=prompt,
            model=model,
            tools=[],
            chat_session_key=None,
            temperature=0.1,
            user_id=user_id,
            tool_choice=None,
            history="",
            response_format=None,
        )
        self.mock_llm_service.ask.assert_called_once_with(mock_ai_request)
        self.mock_ai_response_factory.build_from_llm_response.assert_called_once_with(
            mock_llm_response, mock_ai_request
        )
        self.mock_ai_call_repository.create.assert_called_once_with(mock_ai_response, user_id)
        self.assertEqual(result, "response_123")

    def test_execute_with_all_parameters(self):
        """Test that execute handles all optional parameters correctly."""
        # Arrange
        prompt = ["Test prompt"]
        user_id = 1
        model = "test-model"
        tools = [{"name": "tool1"}]
        chat_session_key = "session_123"
        temperature = 0.5
        tool_choice = "auto"
        history = "previous conversation"
        response_format = "json_object"
        
        mock_ai_request = Mock(spec=AIRequestDomain)
        mock_llm_response = Mock()
        mock_ai_response = Mock(spec=AIResponseDomain)
        mock_saved_response = Mock(spec=AIResponseDomain)
        mock_saved_response.id = "response_123"
        
        self.mock_ai_request_factory.build.return_value = mock_ai_request
        self.mock_llm_service.ask.return_value = mock_llm_response
        self.mock_ai_response_factory.build_from_llm_response.return_value = mock_ai_response
        self.mock_ai_call_repository.create.return_value = mock_saved_response

        # Act
        result = self.use_case.execute(
            prompt, user_id, model=model, tools=tools, chat_session_key=chat_session_key,
            temperature=temperature, tool_choice=tool_choice, history=history,
            response_format=response_format
        )

        # Assert
        self.mock_ai_request_factory.build.assert_called_once_with(
            prompt=prompt,
            model=model,
            tools=tools,
            chat_session_key=chat_session_key,
            temperature=temperature,
            user_id=user_id,
            tool_choice=tool_choice,
            history=history,
            response_format=response_format,
        )
        self.assertEqual(result, "response_123")

    def test_ask_ai_handles_llm_gateway_exception(self):
        """Test that ask_ai handles LLMGatewayException and returns empty response."""
        # Arrange
        mock_ai_request = Mock(spec=AIRequestDomain)
        mock_empty_response = Mock(spec=AIResponseDomain)
        
        self.mock_llm_service.ask.side_effect = LLMGatewayException("API Error")
        self.mock_ai_request_factory.build_empty_response.return_value = mock_empty_response

        # Act
        result = self.use_case.ask_ai(mock_ai_request)

        # Assert
        self.mock_llm_service.ask.assert_called_once_with(mock_ai_request)
        self.mock_ai_request_factory.build_empty_response.assert_called_once_with(mock_ai_request)
        self.assertEqual(result, mock_empty_response)

    def test_ask_ai_returns_response_on_success(self):
        """Test that ask_ai returns AI response on successful LLM call."""
        # Arrange
        mock_ai_request = Mock(spec=AIRequestDomain)
        mock_llm_response = Mock()
        mock_ai_response = Mock(spec=AIResponseDomain)
        
        self.mock_llm_service.ask.return_value = mock_llm_response
        self.mock_ai_response_factory.build_from_llm_response.return_value = mock_ai_response

        # Act
        result = self.use_case.ask_ai(mock_ai_request)

        # Assert
        self.mock_llm_service.ask.assert_called_once_with(mock_ai_request)
        self.mock_ai_response_factory.build_from_llm_response.assert_called_once_with(
            mock_llm_response, mock_ai_request
        )
        self.assertEqual(result, mock_ai_response)

