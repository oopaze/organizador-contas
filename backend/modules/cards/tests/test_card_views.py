from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.cards.models import Card
from modules.cards.views import CardViewSet


class TestCardViewErrors(SimpleTestCase):
    def setUp(self):
        self.view = CardViewSet()
        self.view.container = Mock()
        self.request = Mock()
        self.request.user.id = 7
        self.request.data = {}

    def test_partial_update_returns_404_for_missing_card(self):
        self.view.container.update_card_use_case.return_value.execute.side_effect = Card.DoesNotExist

        response = self.view.partial_update(self.request, pk="999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Cartão não encontrado"})

    def test_set_active_returns_404_for_missing_card(self):
        self.view.container.set_card_active_use_case.return_value.execute.side_effect = Card.DoesNotExist

        response = self.view.set_active(self.request, pk="999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Cartão não encontrado"})

    def test_create_returns_400_for_invalid_payload(self):
        self.view.container.create_card_use_case.return_value.execute.side_effect = ValueError(
            "name é obrigatório"
        )

        response = self.view.create(self.request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "name é obrigatório"})

    def test_partial_update_returns_400_for_invalid_payload(self):
        self.view.container.update_card_use_case.return_value.execute.side_effect = ValueError(
            "due_day deve estar entre 1 e 31"
        )

        response = self.view.partial_update(self.request, pk="1")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "due_day deve estar entre 1 e 31"})
