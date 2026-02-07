#!/bin/bash

# Script to run the divide-for-actor test cases

echo "🧪 Running divide-for-actor test cases..."
echo ""

# Make sure database is running
echo "📦 Starting database..."
docker compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run the specific test cases
echo ""
echo "🔬 Running tests..."
docker compose exec -T backend python manage.py test \
  modules.transactions.tests.test_update_sub_transaction_use_case.TestUpdateSubTransactionUseCase.test_divide_for_actor_preserves_original_actor_and_creates_new_for_specified_actor \
  modules.transactions.tests.test_update_sub_transaction_use_case.TestUpdateSubTransactionUseCase.test_divide_for_actor_when_original_already_has_different_actor \
  -v 2

echo ""
echo "✅ Tests completed!"

