from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.cards.domains.card import CardDomain
from modules.cards.use_cases.card.create import CreateCardUseCase
from modules.cards.use_cases.card.list import ListCardsUseCase
from modules.cards.use_cases.card.set_active import SetCardActiveUseCase
from modules.cards.use_cases.card.update import UpdateCardUseCase


class TestCreateCardUseCase(SimpleTestCase):
    def test_builds_with_user_and_serializes(self):
        repository = Mock()
        factory = Mock()
        serializer = Mock()
        factory.build.return_value = CardDomain(name="Nubank", due_day=10, user_id=7)
        repository.create.return_value = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)
        serializer.serialize.return_value = {"id": 1}

        result = CreateCardUseCase(repository, factory, serializer).execute(
            {"name": "Nubank", "due_day": 10}, user_id=7
        )

        built = factory.build.call_args[0][0]
        self.assertEqual(built["user_id"], 7)
        self.assertEqual(built["name"], "Nubank")
        self.assertEqual(result, {"id": 1})

    def test_rejects_blank_name(self):
        repository = Mock()
        factory = Mock()
        serializer = Mock()

        with self.assertRaises(ValueError):
            CreateCardUseCase(repository, factory, serializer).execute(
                {"name": "   ", "due_day": 10}, user_id=7
            )

        factory.build.assert_not_called()
        repository.create.assert_not_called()

    def test_rejects_non_integer_due_day(self):
        with self.assertRaises(ValueError):
            CreateCardUseCase(Mock(), Mock(), Mock()).execute(
                {"name": "Nubank", "due_day": "abc"}, user_id=7
            )

    def test_rejects_due_day_out_of_range(self):
        use_case = CreateCardUseCase(Mock(), Mock(), Mock())

        with self.assertRaises(ValueError):
            use_case.execute({"name": "Nubank", "due_day": 0}, user_id=7)
        with self.assertRaises(ValueError):
            use_case.execute({"name": "Nubank", "due_day": 32}, user_id=7)

    def test_normalizes_name_and_due_day(self):
        repository = Mock()
        factory = Mock()
        serializer = Mock()
        factory.build.return_value = CardDomain(name="Nubank", due_day=10, user_id=7)
        repository.create.return_value = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)

        CreateCardUseCase(repository, factory, serializer).execute(
            {"name": "  Nubank  ", "due_day": "10"}, user_id=7
        )

        built = factory.build.call_args[0][0]
        self.assertEqual(built["name"], "Nubank")
        self.assertEqual(built["due_day"], 10)


class TestListCardsUseCase(SimpleTestCase):
    def test_lists_scoped_to_user(self):
        repository = Mock()
        serializer = Mock()
        repository.get_all.return_value = [CardDomain(id=1, name="Nubank")]
        serializer.serialize.return_value = {"id": 1}

        result = ListCardsUseCase(repository, serializer).execute(7)

        repository.get_all.assert_called_once_with(7)
        self.assertEqual(result, [{"id": 1}])


class TestUpdateCardUseCase(SimpleTestCase):
    def test_updates_and_serializes(self):
        repository = Mock()
        serializer = Mock()
        card = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)
        repository.get.return_value = card
        repository.update.return_value = card
        serializer.serialize.return_value = {"id": 1}

        UpdateCardUseCase(repository, serializer).execute(1, {"due_day": 12}, user_id=7)

        self.assertEqual(card.due_day, 12)
        repository.update.assert_called_once_with(card)

    def test_rejects_blank_name(self):
        repository = Mock()
        card = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)
        repository.get.return_value = card

        with self.assertRaises(ValueError):
            UpdateCardUseCase(repository, Mock()).execute(1, {"name": "  "}, user_id=7)

        repository.update.assert_not_called()

    def test_rejects_due_day_out_of_range(self):
        repository = Mock()
        card = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)
        repository.get.return_value = card

        with self.assertRaises(ValueError):
            UpdateCardUseCase(repository, Mock()).execute(1, {"due_day": 42}, user_id=7)

        repository.update.assert_not_called()

    def test_normalizes_name_on_update(self):
        repository = Mock()
        serializer = Mock()
        card = CardDomain(id=1, name="Nubank", due_day=10, user_id=7)
        repository.get.return_value = card
        repository.update.return_value = card

        UpdateCardUseCase(repository, serializer).execute(
            1, {"name": "  Nubank  ", "due_day": 12}, user_id=7
        )

        self.assertEqual(card.name, "Nubank")
        self.assertEqual(card.due_day, 12)


class TestSetCardActiveUseCase(SimpleTestCase):
    def test_toggles_active(self):
        repository = Mock()
        serializer = Mock()
        card = CardDomain(id=1, name="Nubank", is_active=True, user_id=7)
        repository.get.return_value = card
        repository.update.return_value = card
        serializer.serialize.return_value = {"id": 1, "is_active": False}

        SetCardActiveUseCase(repository, serializer).execute(1, False, user_id=7)

        self.assertFalse(card.is_active)
        repository.update.assert_called_once_with(card)
