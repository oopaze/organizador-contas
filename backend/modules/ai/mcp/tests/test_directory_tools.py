from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.tools.directory import call_list_actors, call_list_cards


class TestListCardsTool(SimpleTestCase):
    def test_maps_card_fields(self):
        use_case = Mock()
        use_case.execute.return_value = [
            {"id": 1, "name": "Nubank", "due_day": 10, "is_active": True, "extra": "x"}
        ]

        result = call_list_cards(arguments={}, use_case=use_case, user_id=7)

        use_case.execute.assert_called_once_with(7)
        self.assertEqual(
            result["cards"], [{"id": 1, "name": "Nubank", "due_day": 10, "is_active": True}]
        )


class TestListActorsTool(SimpleTestCase):
    def test_maps_actor_fields(self):
        use_case = Mock()
        use_case.execute.return_value = [{"id": 3, "name": "Giovanna", "total_spent": "999.00"}]

        result = call_list_actors(arguments={}, use_case=use_case, user_id=7)

        use_case.execute.assert_called_once_with(7, without_sub_transactions=True)
        self.assertEqual(result["actors"], [{"id": 3, "name": "Giovanna"}])
