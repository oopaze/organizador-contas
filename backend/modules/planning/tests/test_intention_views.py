from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.planning.views import PurchaseIntentionViewSet


class TestPurchaseIntentionViewSet(SimpleTestCase):
    def setUp(self):
        self.view = PurchaseIntentionViewSet()
        self.view.container = Mock()
        self.request = Mock()
        self.request.user.id = 7
        self.request.data = {"status": "dismissed"}

    def test_partial_update_delegates_to_update_use_case(self):
        self.view.container.update_intention_use_case.return_value.execute.return_value = {
            "id": 1,
            "status": "dismissed",
        }

        response = self.view.partial_update(self.request, pk="1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": 1, "status": "dismissed"})
        self.view.container.update_intention_use_case.return_value.execute.assert_called_once_with(
            "1", {"status": "dismissed"}, 7
        )
