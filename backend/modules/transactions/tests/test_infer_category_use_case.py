from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.use_cases.transaction.infer_category import (
    InferTransactionCategoryUseCase,
)


class TestInferTransactionCategoryUseCase(SimpleTestCase):
    def setUp(self):
        self.ai_call_repository = Mock()
        self.ask_use_case = Mock()
        self.ask_use_case.execute.return_value = 1
        self.use_case = InferTransactionCategoryUseCase(
            ai_call_repository=self.ai_call_repository,
            ask_use_case=self.ask_use_case,
        )

    def _ai_response(self, response):
        ai_call = Mock()
        ai_call.response = response
        self.ai_call_repository.get.return_value = ai_call

    def test_returns_inferred_category(self):
        self._ai_response({"category": "food_grocery"})

        result = self.use_case.execute("Padaria", user_id=7)

        self.assertEqual(result, "food_grocery")
        self.ask_use_case.execute.assert_called_once()
        self.assertEqual(self.ask_use_case.execute.call_args[0][1], 7)

    def test_accepts_list_response(self):
        self._ai_response([{"category": "transport_apps"}])

        self.assertEqual(self.use_case.execute("Uber", user_id=7), "transport_apps")

    def test_falls_back_to_other_on_invalid_category(self):
        self._ai_response({"category": "nao_existe"})

        self.assertEqual(self.use_case.execute("Padaria", user_id=7), "other")

    def test_falls_back_to_other_on_malformed_response(self):
        self._ai_response("texto solto")

        self.assertEqual(self.use_case.execute("Padaria", user_id=7), "other")

    def test_skips_ai_for_empty_description(self):
        self.assertEqual(self.use_case.execute("  ", user_id=7), "other")
        self.ask_use_case.execute.assert_not_called()
