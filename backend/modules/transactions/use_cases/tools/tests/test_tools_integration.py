"""
Integration tests for AI tools with real database instances.

These tests create actual model instances in the database to verify
that the tools work correctly with real data.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from modules.transactions.models import Transaction, SubTransaction, Actor
from modules.transactions.container import TransactionsContainer

User = get_user_model()


class TestGetTransactionsToolIntegration(TestCase):
    """Integration tests for GetTransactionsToolUseCase with real database."""

    def setUp(self):
        """Set up test fixtures with real database instances."""
        # Create a test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create transactions
        self.transaction1 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-15",
            total_amount=Decimal("150.00"),
            transaction_identifier="Electricity Bill",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        self.transaction2 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-20",
            total_amount=Decimal("200.00"),
            transaction_identifier="Water Bill",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        self.transaction3 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-01",
            total_amount=Decimal("5000.00"),
            transaction_identifier="Salary",
            transaction_type=Transaction.TransactionType.INCOMING,
            is_salary=True,
        )

        # Initialize the use case from container
        container = TransactionsContainer()
        self.use_case = container.get_transactions_tool_use_case(user_id=self.user.id)

    def test_get_all_transactions_in_period(self):
        """Test getting all transactions in a specific period."""
        result = self.use_case.execute(
            transaction_type=None,
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)
        
        # Verify all transactions are in the result
        self.assertIn("Electricity Bill", result)
        self.assertIn("Water Bill", result)
        self.assertIn("Salary", result)

    def test_get_outgoing_transactions_only(self):
        """Test filtering by outgoing transaction type."""
        result = self.use_case.execute(
            transaction_type="outgoing",
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)
        
        # Verify only outgoing transactions are in the result
        self.assertIn("Electricity Bill", result)
        self.assertIn("Water Bill", result)
        self.assertNotIn("Salary", result)

    def test_get_incoming_transactions_only(self):
        """Test filtering by incoming transaction type."""
        result = self.use_case.execute(
            transaction_type="incoming",
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)
        
        # Verify only incoming transactions are in the result
        self.assertIn("Salary", result)
        self.assertNotIn("Electricity Bill", result)
        self.assertNotIn("Water Bill", result)

    def test_get_transactions_empty_period(self):
        """Test getting transactions when period has no data."""
        result = self.use_case.execute(
            transaction_type=None,
            due_date_start="2026-04-01",
            due_date_end="2026-04-30",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)


class TestGetActorsToolIntegration(TestCase):
    """Integration tests for GetActorsToolUseCase with real database."""

    def setUp(self):
        """Set up test fixtures with real database instances."""
        # Create a test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create actors
        self.actor1 = Actor.objects.create(
            user=self.user,
            name="John Doe"
        )

        self.actor2 = Actor.objects.create(
            user=self.user,
            name="Jane Smith"
        )

        # Create a transaction
        self.transaction = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-15",
            total_amount=Decimal("300.00"),
            transaction_identifier="Shared Expenses",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        # Create sub-transactions with actors
        self.sub_transaction1 = SubTransaction.objects.create(
            transaction=self.transaction,
            actor=self.actor1,
            date="2026-03-15",
            description="John's share",
            amount=Decimal("150.00"),
            installment_info="1/1",
        )

        self.sub_transaction2 = SubTransaction.objects.create(
            transaction=self.transaction,
            actor=self.actor2,
            date="2026-03-15",
            description="Jane's share",
            amount=Decimal("150.00"),
            installment_info="1/1",
        )

        # Initialize the use case from container
        container = TransactionsContainer()
        self.use_case = container.get_actors_tool_use_case(user_id=self.user.id)

    def test_get_actors_with_sub_transactions(self):
        """Test getting actors with their sub-transactions in a period."""
        result = self.use_case.execute(
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)

        # Verify both actors are in the result
        self.assertIn("John Doe", result)
        self.assertIn("Jane Smith", result)

        # Verify amounts are in the result
        self.assertIn("150", result)

    def test_get_actors_empty_period(self):
        """Test getting actors when period has no data."""
        result = self.use_case.execute(
            due_date_start="2026-04-01",
            due_date_end="2026-04-30",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)


class TestGetActorDetailToolIntegration(TestCase):
    """Integration tests for GetActorDetailToolUseCase with real database."""

    def setUp(self):
        """Set up test fixtures with real database instances."""
        # Create a test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create an actor
        self.actor = Actor.objects.create(
            user=self.user,
            name="John Doe"
        )

        # Create transactions
        self.transaction1 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-15",
            total_amount=Decimal("200.00"),
            transaction_identifier="Groceries",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        self.transaction2 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-20",
            total_amount=Decimal("100.00"),
            transaction_identifier="Restaurant",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        # Create sub-transactions for the actor
        self.sub_transaction1 = SubTransaction.objects.create(
            transaction=self.transaction1,
            actor=self.actor,
            date="2026-03-15",
            description="Groceries - John's share",
            amount=Decimal("100.00"),
            installment_info="1/1",
        )

        self.sub_transaction2 = SubTransaction.objects.create(
            transaction=self.transaction2,
            actor=self.actor,
            date="2026-03-20",
            description="Restaurant - John's share",
            amount=Decimal("50.00"),
            installment_info="1/1",
        )

        # Initialize the use case from container
        container = TransactionsContainer()
        self.use_case = container.get_actor_detail_tool_use_case(user_id=self.user.id)

    def test_get_actor_detail_with_sub_transactions(self):
        """Test getting actor detail with sub-transactions."""
        result = self.use_case.execute(
            actor_id=str(self.actor.id),
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)

        # Verify actor name is in the result
        self.assertIn("John Doe", result)

        # Verify sub-transactions are in the result
        self.assertIn("Groceries", result)
        self.assertIn("Restaurant", result)

    def test_get_actor_detail_empty_period(self):
        """Test getting actor detail when period has no data."""
        result = self.use_case.execute(
            actor_id=str(self.actor.id),
            due_date_start="2026-04-01",
            due_date_end="2026-04-30",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)

        # Verify actor name is still in the result
        self.assertIn("John Doe", result)


class TestGetSubTransactionsFromTransactionToolIntegration(TestCase):
    """Integration tests for GetSubTransactionsFromTransactionToolUseCase with real database."""

    def setUp(self):
        """Set up test fixtures with real database instances."""
        # Create a test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create an actor
        self.actor = Actor.objects.create(
            user=self.user,
            name="John Doe"
        )

        # Create a transaction
        self.transaction = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-15",
            total_amount=Decimal("300.00"),
            transaction_identifier="Shared Bill",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        # Create sub-transactions
        self.sub_transaction1 = SubTransaction.objects.create(
            transaction=self.transaction,
            actor=self.actor,
            date="2026-03-15",
            description="Item 1",
            amount=Decimal("100.00"),
            installment_info="1/1",
        )

        self.sub_transaction2 = SubTransaction.objects.create(
            transaction=self.transaction,
            actor=None,
            date="2026-03-15",
            description="Item 2",
            amount=Decimal("200.00"),
            installment_info="1/1",
        )

        # Initialize the use case from container
        container = TransactionsContainer()
        self.use_case = container.get_sub_transactions_from_transaction_tool_use_case(user_id=self.user.id)

    def test_get_sub_transactions_from_transaction(self):
        """Test getting sub-transactions from a transaction."""
        result = self.use_case.execute(transaction_id=self.transaction.id)

        # Verify result is a string
        self.assertIsInstance(result, str)

        # Verify transaction ID is in the result
        self.assertIn(str(self.transaction.id), result)

        # Verify sub-transactions are in the result
        self.assertIn("Item 1", result)
        self.assertIn("Item 2", result)


class TestGetUserGeneralStatsToolIntegration(TestCase):
    """Integration tests for GetUserGeneralStatsToolUseCase with real database."""

    def setUp(self):
        """Set up test fixtures with real database instances."""
        # Create a test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create an actor
        self.actor = Actor.objects.create(
            user=self.user,
            name="John Doe"
        )

        # Create incoming transaction (salary)
        self.income = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-01",
            total_amount=Decimal("5000.00"),
            transaction_identifier="Salary",
            transaction_type=Transaction.TransactionType.INCOMING,
            is_salary=True,
        )

        # Create outgoing transactions
        self.expense1 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-15",
            total_amount=Decimal("1000.00"),
            transaction_identifier="Rent",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        self.expense2 = Transaction.objects.create(
            user=self.user,
            due_date="2026-03-20",
            total_amount=Decimal("500.00"),
            transaction_identifier="Groceries",
            transaction_type=Transaction.TransactionType.OUTGOING,
        )

        # Create sub-transaction with actor
        SubTransaction.objects.create(
            transaction=self.expense2,
            actor=self.actor,
            date="2026-03-20",
            description="John's groceries",
            amount=Decimal("200.00"),
            installment_info="1/1",
        )

        # Initialize the use case from container
        container = TransactionsContainer()
        self.use_case = container.get_user_general_stats_tool_use_case(user_id=self.user.id)

    def test_get_user_general_stats(self):
        """Test getting user general stats."""
        result = self.use_case.execute(
            due_date_start="2026-03-01",
            due_date_end="2026-03-31",
        )

        # Verify result is a string
        self.assertIsInstance(result, str)

        # Verify stats are in the result
        self.assertIn("5000", result)  # Income
        self.assertIn("1500", result)  # Total expenses (1000 + 500)
        self.assertIn("3500", result)  # Balance (5000 - 1500)

