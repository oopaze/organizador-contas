from unittest.mock import Mock
from django.test import TestCase, SimpleTestCase

from modules.transactions.use_cases.actor.delete import DeleteActorUseCase


class TestDeleteActorUseCase(TestCase):
    """Test DeleteActorUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()

        self.use_case = DeleteActorUseCase(
            actor_repository=self.mock_actor_repository,
        )

    def test_delete_actor(self):
        """Test deleting an actor."""
        # Arrange
        actor_id = 1
        user_id = 1

        # Act
        self.use_case.execute(actor_id, user_id)

        # Assert
        self.mock_actor_repository.delete.assert_called_once_with(actor_id, user_id)

    def test_delete_actor_different_user(self):
        """Test deleting an actor for a different user."""
        # Arrange
        actor_id = 2
        user_id = 2

        # Act
        self.use_case.execute(actor_id, user_id)

        # Assert
        self.mock_actor_repository.delete.assert_called_once_with(actor_id, user_id)


class TestDeleteActorBlocksWithActiveLoans(SimpleTestCase):
    def test_raises_when_actor_has_active_loans(self):
        actor_repo = Mock()
        loan_repo = Mock()
        loan_repo.has_active_for_actor.return_value = True

        use_case = DeleteActorUseCase(
            actor_repository=actor_repo,
            loan_repository=loan_repo,
        )

        with self.assertRaises(ValueError) as cm:
            use_case.execute(actor_id=10, user_id=7)
        self.assertIn("empréstimos ativos", str(cm.exception).lower())
        actor_repo.delete.assert_not_called()

    def test_proceeds_when_no_active_loans(self):
        actor_repo = Mock()
        loan_repo = Mock()
        loan_repo.has_active_for_actor.return_value = False

        use_case = DeleteActorUseCase(actor_repository=actor_repo, loan_repository=loan_repo)
        use_case.execute(actor_id=10, user_id=7)

        actor_repo.delete.assert_called_once_with(10, 7)
