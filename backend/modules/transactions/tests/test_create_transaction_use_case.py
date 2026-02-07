from unittest.mock import Mock, MagicMock
from django.test import TestCase

from modules.transactions.use_cases.transaction.create import CreateTransactionUseCase
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class TestCreateTransactionUseCase(TestCase):
    """Test CreateTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_transaction_serializer = Mock()
        self.mock_transaction_factory = Mock()
        self.mock_sub_transaction_factory = Mock()
        self.mock_sub_transaction_repository = Mock()

        self.use_case = CreateTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
            transaction_factory=self.mock_transaction_factory,
            sub_transaction_factory=self.mock_sub_transaction_factory,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_create_non_recurrent_transaction(self):
        """Test creating a non-recurrent transaction."""
        # Arrange
        data = {
            "due_date": "2026-03-15",
            "total_amount": 150.00,
            "transaction_identifier": "Electricity Bill",
            "transaction_type": "outgoing",
            "user_id": 1,
            "is_recurrent": False,
            "is_salary": False,
        }

        mock_transaction = TransactionDomain(
            id=1,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Electricity Bill",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=False,
            is_salary=False,
        )

        mock_sub_transaction = SubTransactionDomain(
            id=1,
            date="2026-03-15",
            description="Electricity Bill",
            amount=150.00,
            installment_info="1/1",
        )

        self.mock_transaction_factory.build.return_value = mock_transaction
        self.mock_transaction_repository.create.return_value = mock_transaction
        self.mock_sub_transaction_factory.build_from_transaction.return_value = mock_sub_transaction
        self.mock_sub_transaction_repository.create.return_value = mock_sub_transaction
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Electricity Bill"}

        # Act
        result = self.use_case.execute(data)

        # Assert
        self.mock_transaction_factory.build.assert_called_once_with(data)
        self.mock_transaction_repository.create.assert_called_once_with(mock_transaction)
        self.mock_sub_transaction_factory.build_from_transaction.assert_called_once_with(mock_transaction, "1/1")
        self.mock_sub_transaction_repository.create.assert_called_once_with(mock_sub_transaction)
        self.mock_transaction_serializer.serialize.assert_called_once_with(mock_transaction)
        self.assertEqual(result, {"id": 1, "transaction_identifier": "Electricity Bill"})

    def test_create_salary_transaction_no_sub_transaction(self):
        """Test creating a salary transaction does not create sub-transaction."""
        # Arrange
        data = {
            "due_date": "2026-03-01",
            "total_amount": 5000.00,
            "transaction_identifier": "Monthly Salary",
            "transaction_type": "incoming",
            "user_id": 1,
            "is_recurrent": False,
            "is_salary": True,
        }

        mock_transaction = TransactionDomain(
            id=2,
            due_date="2026-03-01",
            total_amount=5000.00,
            transaction_identifier="Monthly Salary",
            transaction_type="incoming",
            user_id=1,
            is_recurrent=False,
            is_salary=True,
        )

        self.mock_transaction_factory.build.return_value = mock_transaction
        self.mock_transaction_repository.create.return_value = mock_transaction
        self.mock_transaction_serializer.serialize.return_value = {"id": 2, "transaction_identifier": "Monthly Salary"}

        # Act
        result = self.use_case.execute(data)

        # Assert
        self.mock_transaction_factory.build.assert_called_once_with(data)
        self.mock_transaction_repository.create.assert_called_once_with(mock_transaction)
        # Should NOT create sub-transaction for salary
        self.mock_sub_transaction_factory.build_from_transaction.assert_not_called()
        self.mock_sub_transaction_repository.create.assert_not_called()
        self.mock_transaction_serializer.serialize.assert_called_once_with(mock_transaction)
        self.assertEqual(result, {"id": 2, "transaction_identifier": "Monthly Salary"})

    def test_create_recurrent_transaction(self):
        """Test creating a recurrent transaction creates multiple installments."""
        # Arrange
        data = {
            "due_date": "2026-03-15",
            "total_amount": 100.00,
            "transaction_identifier": "Gym Membership",
            "transaction_type": "outgoing",
            "user_id": 1,
            "is_recurrent": True,
            "recurrence_count": 3,
            "is_salary": False,
        }

        # Mock transactions for each installment
        mock_transactions = []
        for i in range(3):
            mock_transaction = TransactionDomain(
                id=i + 1,
                due_date=f"2026-0{3+i}-15",
                total_amount=100.00,
                transaction_identifier="Gym Membership",
                transaction_type="outgoing",
                user_id=1,
                is_recurrent=True,
                installment_number=i + 1,
                main_transaction=1 if i > 0 else None,
                recurrence_count=3,
            )
            mock_transactions.append(mock_transaction)

        self.mock_transaction_factory.build.side_effect = mock_transactions
        self.mock_transaction_repository.create.side_effect = mock_transactions
        self.mock_sub_transaction_repository.create.return_value = Mock()
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Gym Membership"}

        # Act
        result = self.use_case.execute(data)

        # Assert
        self.assertEqual(self.mock_transaction_factory.build.call_count, 3)
        self.assertEqual(self.mock_transaction_repository.create.call_count, 3)
        self.assertEqual(self.mock_sub_transaction_repository.create.call_count, 3)
        self.mock_transaction_serializer.serialize.assert_called_once_with(mock_transactions[0])
        self.assertEqual(result, {"id": 1, "transaction_identifier": "Gym Membership"})

    def test_calculate_next_due_date(self):
        """Test date calculation for recurrent transactions."""
        # Test moving from March to April
        next_date = self.use_case.calculate_next_due_date("2026-03-15")
        self.assertEqual(next_date, "2026-04-15")

        # Test moving from December to January (year change)
        next_date = self.use_case.calculate_next_due_date("2026-12-31")
        self.assertEqual(next_date, "2027-01-31")

