# Cartões, fatura mensal garantida e vínculo fatura↔cartão — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cadastro de cartões (nome + dia de vencimento), fatura em aberto garantida por cartão todo mês (mesmo zerada) e upload da fatura vinculado ao cartão, estreitando a conciliação.

**Architecture:** Módulo novo `modules/cards` com `Card` e CRUD; FK opcional `Transaction.card`; `EnsureMonthlyCardBillsUseCase` idempotente (padrão do `EnsureMonthlySalaryUseCase`); quick add e MCP passam a referenciar o cartão; upload grava `card_id` na fatura importada e a conciliação filtra candidatas pelo cartão. Migração de dados vincula faturas antigas pelo identificador.

**Tech Stack:** Django 6 + DRF + dependency_injector, pytest (`DJANGO_SETTINGS_MODULE=infra.settings`), React 18 + TypeScript + Vite + Tailwind + shadcn/ui, yarn.

**Spec:** [docs/superpowers/specs/2026-09-14-cartoes-e-fatura-mensal-design.md](../specs/2026-09-14-cartoes-e-fatura-mensal-design.md)

---

## Global Constraints

- **Sem hard delete de cartão**: desativar via `is_active=False`.
- **Uma fatura por cartão/mês**: chave `card_id` + `due_date__year`/`month`; nunca duplicar.
- **Fatura importada carrega `card_id` opcional**; sem cartão, conciliação mantém o comportamento atual (janela de datas).
- **`card_label` legado** (MCP/cliente antigo) continua funcionando: resolve pelo nome; sem cartão cadastrado, cai no comportamento antigo.
- **Backfill normaliza nomes** com `strip()` + `casefold()`.
- **Valores em Decimal no backend; JSON expõe string**; datas em ISO.
- **Todo texto de UI em pt-BR.**
- **Frontend usa `yarn`**, nunca npm.
- **Testes de use case seguem o padrão do módulo:** `unittest.mock.Mock`, `django.test.TestCase`/`SimpleTestCase`.
- **DjangoJSONEncoder nas respostas do MCP** (datas/decimais).

---

## Estrutura de arquivos

**Backend — criados:**

```
modules/cards/__init__.py
modules/cards/apps.py
modules/cards/models.py
modules/cards/domains/__init__.py
modules/cards/domains/card.py
modules/cards/factories/__init__.py
modules/cards/factories/card.py
modules/cards/repositories/__init__.py
modules/cards/repositories/card.py
modules/cards/serializers/__init__.py
modules/cards/serializers/card.py
modules/cards/use_cases/__init__.py
modules/cards/use_cases/card/__init__.py
modules/cards/use_cases/card/create.py
modules/cards/use_cases/card/list.py
modules/cards/use_cases/card/update.py
modules/cards/use_cases/card/set_active.py
modules/cards/container.py
modules/cards/views.py
modules/cards/urls.py
modules/cards/migrations/__init__.py
modules/cards/tests/__init__.py
modules/cards/tests/test_card_use_cases.py
modules/transactions/services/card_naming.py
modules/transactions/use_cases/transaction/ensure_card_bills.py
modules/transactions/tests/test_ensure_card_bills_use_case.py
modules/transactions/tests/test_transaction_card_support.py
modules/transactions/migrations/0017_backfill_cards.py
```

**Backend — modificados:**

- `modules/transactions/models.py` — FK `card`.
- `modules/transactions/domains/transaction.py`, `factories/transaction.py`, `serializers/transaction.py`, `repositories/transaction.py`.
- `modules/transactions/use_cases/transaction/quick_add.py` (suporte a cartão) e `reconcile_bill_preview.py` (filtro por cartão).
- `modules/transactions/use_cases/transaction/__init__.py`, `use_cases/__init__.py`, `container.py`, `views.py`.
- `modules/file_reader/domains/bill.py`, `factories/bill.py`, `repositories/bill.py`, `use_cases/transpose_file_bill_to_models.py`, `use_cases/upload_file.py`, `views.py`.
- `infra/settings.py` (INSTALLED_APPS), `infra/urls.py` (`/cards/`).
- `modules/ai/mcp/tools/__init__.py` + `tools/transactions.py` (`card_id` no create).

**Frontend — criados:**

```
services/cards/getCards.ts
services/cards/createCard.ts
services/cards/updateCard.ts
services/cards/setCardActive.ts
services/transactions/ensureCardBills.ts
```

**Frontend — modificados:**

- `services/types.ts`, `services/index.ts`, `services/bills/uploadBill.ts`.
- `app/pages/settings-page.tsx` (seção Cartões).
- `app/components/upload-bill-dialog.tsx` (select de cartão + sugestão + novo cartão).
- `app/pages/dashboard-page.tsx`, `app/pages/planning-page.tsx` (`ensureCardBills`).

---

## Sobre testes neste plano

Backend: testes unitários por use case com dependências mockadas, mais os ajustes nos testes existentes. Comandos (ambiente com Postgres):

```bash
cd backend && pytest modules/transactions/tests modules/file_reader/tests modules/cards/tests -q
```

Frontend: sem suíte nova; verificação é `yarn build` + `yarn test` + checklist manual.

---

## Phase 1 — Cartões (módulo novo)

### Task 1: Módulo `cards` com CRUD

**Files:**
- Create: `backend/modules/cards/` (todos os arquivos de `models` a `urls` listados acima, exceto migrations/tests)
- Create: `backend/modules/cards/tests/test_card_use_cases.py`
- Modify: `backend/infra/settings.py`, `backend/infra/urls.py`

**Interfaces:**
- Produces: `CardRepository.get(card_id, user_id)`, `get_by_name(user_id, name)`, `get_all(user_id, only_active=False)`, `create(card)`, `update(card)`, `delete(card_id, user_id)`; endpoints `GET/POST /cards/cards/`, `PATCH /cards/cards/{id}/`, `POST /cards/cards/{id}/set_active/`.

- [ ] **Step 1: Modelo, domínio, factory, repositório, serializer**

`backend/modules/cards/models.py`:

```python
from django.db import models

from modules.base.models import SoftDeleteModel, TimedModel, UserOwnedModel


class Card(TimedModel, UserOwnedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    due_day = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
```

`backend/modules/cards/domains/card.py`:

```python
class CardDomain:
    def __init__(
        self,
        name: str = None,
        due_day: int = 1,
        is_active: bool = True,
        id: int = None,
        user_id: int = None,
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.name = name
        self.due_day = due_day
        self.is_active = is_active
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def update(self, data: dict):
        self.name = data.get("name", self.name)
        self.due_day = data.get("due_day", self.due_day)
        self.is_active = data.get("is_active", self.is_active)
```

`backend/modules/cards/factories/card.py`:

```python
from modules.cards.domains.card import CardDomain
from modules.cards.models import Card


class CardFactory:
    def build_from_model(self, model: Card) -> CardDomain:
        return CardDomain(
            id=model.id,
            name=model.name,
            due_day=model.due_day,
            is_active=model.is_active,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def build(self, data: dict) -> CardDomain:
        return CardDomain(
            name=data["name"],
            due_day=data.get("due_day", 1),
            is_active=data.get("is_active", True),
            user_id=data["user_id"],
        )
```

`backend/modules/cards/repositories/card.py`:

```python
from django.utils import timezone

from modules.cards.domains.card import CardDomain
from modules.cards.factories.card import CardFactory
from modules.cards.models import Card


class CardRepository:
    def __init__(self, model: Card, card_factory: CardFactory):
        self.model = model
        self.card_factory = card_factory

    @property
    def queryset(self):
        return (
            self.model.objects
                .order_by("name")
                .exclude(deleted_at__isnull=False)
        )

    def get(self, card_id: int, user_id: int) -> "CardDomain":
        instance = self.queryset.get(id=card_id, user_id=user_id)
        return self.card_factory.build_from_model(instance)

    def get_by_name(self, user_id: int, name: str) -> "CardDomain | None":
        instance = (
            self.queryset
                .filter(user_id=user_id, name__iexact=(name or "").strip())
                .first()
        )
        if instance is None:
            return None
        return self.card_factory.build_from_model(instance)

    def get_all(self, user_id: int, only_active: bool = False) -> list["CardDomain"]:
        filters = {"user_id": user_id}
        if only_active:
            filters["is_active"] = True
        instances = self.queryset.filter(**filters)
        return [self.card_factory.build_from_model(instance) for instance in instances]

    def create(self, card: "CardDomain") -> "CardDomain":
        instance = self.model.objects.create(
            name=card.name,
            due_day=card.due_day,
            is_active=card.is_active,
            user_id=card.user_id,
        )
        instance.refresh_from_db()
        return self.card_factory.build_from_model(instance)

    def update(self, card: "CardDomain") -> "CardDomain":
        instance = self.queryset.get(id=card.id, user_id=card.user_id)
        instance.name = card.name
        instance.due_day = card.due_day
        instance.is_active = card.is_active
        instance.save()
        return self.card_factory.build_from_model(instance)

    def delete(self, card_id: int, user_id: int):
        self.queryset.filter(id=card_id, user_id=user_id).update(deleted_at=timezone.now())
```

`backend/modules/cards/serializers/card.py`:

```python
from modules.cards.domains.card import CardDomain


class CardSerializer:
    def serialize(self, card: "CardDomain") -> dict:
        return {
            "id": card.id,
            "name": card.name,
            "due_day": card.due_day,
            "is_active": card.is_active,
        }
```

`backend/modules/cards/__init__.py`, `domains/__init__.py`, `factories/__init__.py`, `repositories/__init__.py`, `serializers/__init__.py` seguem o padrão do repo (reexportando a classe do módulo).

- [ ] **Step 2: Testes que falham dos use cases**

`backend/modules/cards/tests/test_card_use_cases.py`:

```python
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
```

Run: `pytest modules/cards/tests -q` — Expected: collection error (módulos não existem).

- [ ] **Step 3: Implementar os use cases**

`create.py`:

```python
from modules.cards.factories.card import CardFactory
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class CreateCardUseCase:
    def __init__(self, card_repository: CardRepository, card_factory: CardFactory, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_factory = card_factory
        self.card_serializer = card_serializer

    def execute(self, data: dict, user_id: int) -> dict:
        card = self.card_factory.build({**data, "user_id": user_id})
        created = self.card_repository.create(card)
        return self.card_serializer.serialize(created)
```

`list.py`:

```python
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class ListCardsUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, user_id: int) -> list[dict]:
        cards = self.card_repository.get_all(user_id)
        return [self.card_serializer.serialize(card) for card in cards]
```

`update.py`:

```python
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class UpdateCardUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, card_id: int, data: dict, user_id: int) -> dict:
        card = self.card_repository.get(card_id, user_id)
        card.update(data)
        updated = self.card_repository.update(card)
        return self.card_serializer.serialize(updated)
```

`set_active.py`:

```python
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class SetCardActiveUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, card_id: int, is_active: bool, user_id: int) -> dict:
        card = self.card_repository.get(card_id, user_id)
        card.update({"is_active": bool(is_active)})
        updated = self.card_repository.update(card)
        return self.card_serializer.serialize(updated)
```

Run: `pytest modules/cards/tests -q` — Expected: 4 passed.

- [ ] **Step 4: Container, views, urls, settings**

`container.py`:

```python
from dependency_injector import containers, providers

from modules.cards.factories.card import CardFactory
from modules.cards.models import Card
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer
from modules.cards.use_cases import (
    CreateCardUseCase,
    ListCardsUseCase,
    SetCardActiveUseCase,
    UpdateCardUseCase,
)


class CardsContainer(containers.DeclarativeContainer):
    card_factory = providers.Factory(CardFactory)
    card_repository = providers.Factory(CardRepository, model=Card, card_factory=card_factory)
    card_serializer = providers.Factory(CardSerializer)

    create_card_use_case = providers.Factory(
        CreateCardUseCase, card_repository=card_repository, card_factory=card_factory, card_serializer=card_serializer
    )
    list_cards_use_case = providers.Factory(
        ListCardsUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
    update_card_use_case = providers.Factory(
        UpdateCardUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
    set_card_active_use_case = providers.Factory(
        SetCardActiveUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
```

`views.py`:

```python
from rest_framework import decorators, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.cards.container import CardsContainer
from modules.userdata.authentication import JWTAuthentication


class CardViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = CardsContainer()

    def list(self, request):
        return Response(self.container.list_cards_use_case().execute(request.user.id), status=status.HTTP_200_OK)

    def create(self, request):
        card = self.container.create_card_use_case().execute(request.data, request.user.id)
        return Response(card, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        card = self.container.update_card_use_case().execute(pk, request.data, request.user.id)
        return Response(card, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["POST"], url_path="set_active")
    def set_active(self, request, pk: str):
        card = self.container.set_card_active_use_case().execute(
            pk, request.data.get("is_active", False), request.user.id
        )
        return Response(card, status=status.HTTP_200_OK)
```

`urls.py`:

```python
from rest_framework.routers import DefaultRouter

from modules.cards.views import CardViewSet

router = DefaultRouter()
router.register(r"cards", CardViewSet, basename="cards")

urlpatterns = router.urls
```

`infra/urls.py`: adicionar `path("cards/", include("modules.cards.urls")),`.
`infra/settings.py`: adicionar `"modules.cards"` ao `INSTALLED_APPS` (depois de `modules.loans`).

- [ ] **Step 5: Migration e verificação de rotas**

Run: `python manage.py makemigrations cards` — Expected: `0001_initial` criado.
Run: `pytest modules/cards/tests -q` — Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/modules/cards backend/infra
git commit -m "feat(cards): cards module with crud endpoints"
```

---

## Phase 2 — FK no Transaction

### Task 2: `Transaction.card` + plumbing

**Files:**
- Modify: `backend/modules/transactions/models.py`, `domains/transaction.py`, `factories/transaction.py`, `serializers/transaction.py`, `repositories/transaction.py`
- Test: `backend/modules/transactions/tests/test_transaction_card_support.py`

**Interfaces:**
- Produces: `TransactionDomain.card_id`; `TransactionSerializer.serialize` com `"card_id"`; `TransactionRepository.create/update` persistindo `card_id`.

- [ ] **Step 1: Testes que falham**

`backend/modules/transactions/tests/test_transaction_card_support.py`:

```python
from datetime import datetime
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import TransactionDomain
from modules.transactions.factories import TransactionFactory
from modules.transactions.serializers import TransactionSerializer


class TestTransactionCardSupport(SimpleTestCase):
    def test_factory_build_reads_card_id(self):
        factory = TransactionFactory()

        transaction = factory.build(
            {
                "due_date": "2026-09-01",
                "total_amount": "100",
                "transaction_identifier": "Fatura Nubank 09/2026",
                "transaction_type": "outgoing",
                "user_id": 7,
                "category": "credit_card",
                "card_id": 3,
            }
        )

        self.assertEqual(transaction.card_id, 3)

    def test_serializer_includes_card_id(self):
        transaction = TransactionDomain(
            id=1,
            due_date="2026-09-01",
            total_amount="100",
            transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing",
            user_id=7,
            category="credit_card",
            card_id=3,
            created_at=datetime(2026, 9, 1),
            updated_at=datetime(2026, 9, 1),
        )
        serializer = TransactionSerializer(sub_transaction_serializer=Mock())

        payload = serializer.serialize(transaction)

        self.assertEqual(payload["card_id"], 3)
```

Run: `pytest modules/transactions/tests/test_transaction_card_support.py -q` — Expected: FAIL (`card_id` não existe).

- [ ] **Step 2: Modelo, domínio, factory, serializer, repositório**

`models.py` (adicionar campo):

```python
    card = models.ForeignKey(
        "cards.Card", on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions"
    )
```

`domains/transaction.py`: adicionar `card_id: int = None` no `__init__` e `self.card_id = card_id`.
`factories/transaction.py`: em `build_from_model` adicionar `card_id=model.card_id`; em `build` adicionar `card_id=data.get("card_id")`.
`serializers/transaction.py`: adicionar `"card_id": transaction.card_id,`.
`repositories/transaction.py`: em `create` adicionar `card_id=transaction.card_id`; em `update` adicionar `transaction_instance.card_id = transaction.card_id`.

- [ ] **Step 3: Migration e testes verdes**

Run: `python manage.py makemigrations transactions` — Expected: `0016_transaction_card` (depende de `cards.0001_initial`).
Run: `pytest modules/transactions/tests -q` — Expected: tudo verde (exceto a falha pré-existente `test_update_transaction_with_single_sub_transaction`).

- [ ] **Step 4: Commit**

```bash
git add backend/modules/transactions
git commit -m "feat(transactions): optional card fk on transactions"
```

---

## Phase 3 — Fatura mensal garantida

### Task 3: `EnsureMonthlyCardBillsUseCase`

**Files:**
- Create: `backend/modules/transactions/use_cases/transaction/ensure_card_bills.py`
- Modify: `backend/modules/transactions/repositories/transaction.py` (`get_open_bill_by_card`), `use_cases/transaction/__init__.py`, `use_cases/__init__.py`, `container.py`, `views.py`
- Test: `backend/modules/transactions/tests/test_ensure_card_bills_use_case.py`

**Interfaces:**
- Consumes: `CardRepository.get_all(user_id, only_active=True)` (Task 1), `TransactionRepository.get_open_bill_by_card(user_id, card_id, year, month)`.
- Produces: `EnsureMonthlyCardBillsUseCase.execute(user_id, month) -> {"bills": [serialized...]}`; endpoint `POST /transactions/transactions/ensure_card_bills/`.

- [ ] **Step 1: Teste que falha**

`backend/modules/transactions/tests/test_ensure_card_bills_use_case.py`:

```python
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.cards.domains.card import CardDomain
from modules.transactions.domains import TransactionDomain
from modules.transactions.use_cases.transaction.ensure_card_bills import EnsureMonthlyCardBillsUseCase


class TestEnsureMonthlyCardBillsUseCase(SimpleTestCase):
    def setUp(self):
        self.card_repository = Mock()
        self.transaction_repository = Mock()
        self.transaction_factory = Mock()
        self.transaction_serializer = Mock()
        self.recalculate_amount_use_case = Mock()
        self.use_case = EnsureMonthlyCardBillsUseCase(
            card_repository=self.card_repository,
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
        )

    def test_creates_zeroed_bill_with_card_due_day(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        self.transaction_repository.get_open_bill_by_card.return_value = None
        built = TransactionDomain(id=50, total_amount="0", user_id=7)
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = built
        self.transaction_repository.get.return_value = built
        self.transaction_serializer.serialize.return_value = {"id": 50}

        result = self.use_case.execute(7, "2026-09")

        self.card_repository.get_all.assert_called_once_with(7, only_active=True)
        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["transaction_identifier"], "Fatura Nubank 09/2026")
        self.assertEqual(built_data["due_date"], "2026-09-10")
        self.assertEqual(built_data["card_id"], 3)
        self.assertEqual(built_data["category"], "credit_card")
        self.recalculate_amount_use_case.execute.assert_called_once_with(50, 7)
        self.assertEqual(result, {"bills": [{"id": 50}]})

    def test_reuses_existing_bill_and_syncs_due_date(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        existing = TransactionDomain(id=50, total_amount="100", user_id=7, due_date="2026-09-01")
        self.transaction_repository.get_open_bill_by_card.return_value = existing
        self.transaction_repository.update.return_value = existing
        self.transaction_repository.get.return_value = existing
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-09")

        self.transaction_repository.create.assert_not_called()
        self.assertEqual(str(existing.due_date), "2026-09-10")
        self.transaction_repository.update.assert_called_once_with(existing)
        self.recalculate_amount_use_case.execute.assert_called_once_with(50, 7)

    def test_clamps_due_day_to_month_end(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=31)]
        self.transaction_repository.get_open_bill_by_card.return_value = None
        built = TransactionDomain(id=50, user_id=7)
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = built
        self.transaction_repository.get.return_value = built
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-02")

        self.assertEqual(self.transaction_factory.build.call_args[0][0]["due_date"], "2026-02-28")
```

Run: `pytest modules/transactions/tests/test_ensure_card_bills_use_case.py -q` — Expected: ImportError.

- [ ] **Step 2: Implementar use case e repositório**

`ensure_card_bills.py`:

```python
import calendar
from datetime import date

from modules.cards.repositories.card import CardRepository
from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.types import TransactionCategory
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase


class EnsureMonthlyCardBillsUseCase:
    """Guarantees one open bill per active card/month, even when zeroed.

    The bill is anchored on the competência month using the card due day
    (clamped to the month end) so the app's monthly filter keeps working.
    Idempotent: one bill per card/month.
    """

    def __init__(
        self,
        card_repository: CardRepository,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
        transaction_serializer: TransactionSerializer,
        recalculate_amount_use_case: RecalculateAmountUseCase,
    ):
        self.card_repository = card_repository
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory
        self.transaction_serializer = transaction_serializer
        self.recalculate_amount_use_case = recalculate_amount_use_case

    def execute(self, user_id: int, month: str) -> dict:
        year, month_number = self._parse_month(month)
        last_day = calendar.monthrange(year, month_number)[1]
        bills = []

        for card in self.card_repository.get_all(user_id, only_active=True):
            due_day = min(max(int(card.due_day or 1), 1), last_day)
            due_date = date(year, month_number, due_day).isoformat()
            identifier = f"Fatura {card.name} {month_number:02d}/{year}"

            bill = self.transaction_repository.get_open_bill_by_card(
                user_id, card.id, year, month_number
            )
            if bill is None:
                bill = self.transaction_factory.build(
                    {
                        "due_date": due_date,
                        "total_amount": 0,
                        "transaction_identifier": identifier,
                        "transaction_type": "outgoing",
                        "is_salary": False,
                        "user_id": user_id,
                        "is_recurrent": False,
                        "category": TransactionCategory.CREDIT_CARD.name,
                        "card_id": card.id,
                    }
                )
                bill = self.transaction_repository.create(bill)
            elif bill.due_date != due_date:
                bill.due_date = due_date
                bill = self.transaction_repository.update(bill)

            self.recalculate_amount_use_case.execute(bill.id, user_id)
            updated = self.transaction_repository.get(bill.id, user_id)
            bills.append(self.transaction_serializer.serialize(updated))

        return {"bills": bills}

    def _parse_month(self, month: str) -> tuple[int, int]:
        try:
            year, month_number = str(month).split("-")
            year, month_number = int(year), int(month_number)
        except (TypeError, ValueError):
            raise ValueError("month deve estar no formato YYYY-MM")
        if month_number < 1 or month_number > 12:
            raise ValueError("month deve estar no formato YYYY-MM")
        return year, month_number
```

`repositories/transaction.py` (novo método, ao lado do `get_open_bill`):

```python
    def get_open_bill_by_card(self, user_id: int, card_id: int, year: int, month: int) -> "TransactionDomain | None":
        instance = self.queryset.filter(
            user_id=user_id,
            card_id=card_id,
            file__isnull=True,
            category=TransactionCategory.CREDIT_CARD.name,
            due_date__year=year,
            due_date__month=month,
        ).first()
        if instance is None:
            return None
        return self.transaction_factory.build_from_model(instance)
```

- [ ] **Step 3: Wiring (exports, container, view)**

- `use_cases/transaction/__init__.py` e `use_cases/__init__.py`: exportar `EnsureMonthlyCardBillsUseCase`.
- `container.py`: importar `CardRepository`/`CardFactory`/`Card` e criar `card_repository`; provider:

```python
    ensure_monthly_card_bills_use_case = providers.Factory(
        EnsureMonthlyCardBillsUseCase,
        card_repository=card_repository,
        transaction_repository=transaction_repository,
        transaction_factory=transaction_factory,
        transaction_serializer=transaction_serializer,
        recalculate_amount_use_case=recalculate_amount_use_case,
    )
```

- `views.py` (ao lado de `ensure_salary`):

```python
    @decorators.action(detail=False, methods=["POST"], url_path="ensure_card_bills")
    def ensure_card_bills(self, request):
        month = request.data.get("month")
        if not month:
            return Response({"error": "month é obrigatório (YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = self.container.ensure_monthly_card_bills_use_case().execute(request.user.id, month)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
```

- [ ] **Step 4: Rodar testes e commit**

Run: `pytest modules/transactions/tests/test_ensure_card_bills_use_case.py -q` — Expected: 3 passed.

```bash
git add backend/modules/transactions
git commit -m "feat(transactions): guarantee monthly card bills"
```

---

## Phase 4 — Quick add e conciliação por cartão

### Task 4: Quick add com cartão (sem duplicar)

**Files:**
- Modify: `backend/modules/transactions/use_cases/transaction/quick_add.py`
- Test: `backend/modules/transactions/tests/test_quick_add_use_case.py`

**Interfaces:**
- Consumes: `CardRepository.get(card_id, user_id)`, `get_by_name(user_id, name)` (Task 1); `get_open_bill_by_card` (Task 3).
- Produces: `QuickAddTransactionUseCase` aceita `card_id` no payload; `card_label` resolve pelo nome (legado).

- [ ] **Step 1: Testes que falham**

Adicionar em `test_quick_add_use_case.py` (novos testes; o `use_case` do setUp continua sem cartão):

```python
    def test_credit_with_card_id_uses_card_due_day(self):
        card_repository = Mock()
        card = CardDomain(id=3, name="Nubank", due_day=10)
        card_repository.get.return_value = card
        use_case = QuickAddTransactionUseCase(
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            create_sub_transaction_use_case=self.create_sub_transaction_use_case,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
            card_repository=card_repository,
        )
        bill = TransactionDomain(id=20, total_amount="0", user_id=7)
        filled = TransactionDomain(id=20, total_amount="54.90", user_id=7)
        self.transaction_repository.get_open_bill_by_card.return_value = None
        self.transaction_factory.build.return_value = bill
        self.transaction_repository.create.return_value = bill
        self.transaction_repository.get.return_value = filled
        self.create_sub_transaction_use_case.execute.return_value = {"id": 60}
        self.transaction_serializer.serialize.return_value = {"id": 20}

        use_case.execute(
            {
                "payment_method": "credit",
                "amount": "54.90",
                "description": "Padaria",
                "date": "2026-09-13",
                "card_id": 3,
            },
            user_id=7,
        )

        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["card_id"], 3)
        self.assertEqual(built_data["due_date"], "2026-09-10")
        self.assertEqual(built_data["transaction_identifier"], "Fatura Nubank 09/2026")
        self.transaction_repository.get_open_bill_by_card.assert_called_once_with(7, 3, 2026, 9)

    def test_credit_with_unknown_card_label_falls_back_to_legacy(self):
        card_repository = Mock()
        card_repository.get_by_name.return_value = None
        use_case = QuickAddTransactionUseCase(
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            create_sub_transaction_use_case=self.create_sub_transaction_use_case,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
            card_repository=card_repository,
        )
        bill = TransactionDomain(id=20, total_amount="0", user_id=7)
        self.transaction_repository.get_open_bill.return_value = None
        self.transaction_factory.build.return_value = bill
        self.transaction_repository.create.return_value = bill
        self.transaction_repository.get.return_value = bill
        self.create_sub_transaction_use_case.execute.return_value = {"id": 60}
        self.transaction_serializer.serialize.return_value = {"id": 20}

        use_case.execute(
            {
                "payment_method": "credit",
                "amount": "10",
                "description": "Café",
                "date": "2026-09-14",
                "card_label": "Visa",
            },
            user_id=7,
        )

        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertIsNone(built_data.get("card_id"))
        self.assertEqual(built_data["due_date"], "2026-09-01")
        self.transaction_repository.get_open_bill.assert_called_once_with(
            7, "Fatura Visa 09/2026", 2026, 9
        )
```

Import necessário no topo do teste: `from modules.cards.domains.card import CardDomain`.

Run: `pytest modules/transactions/tests/test_quick_add_use_case.py -q` — Expected: erros (parâmetro `card_repository` não existe).

- [ ] **Step 2: Implementar no quick add**

`quick_add.py`:

- `__init__` recebe `card_repository=None` e guarda.
- Novo helper:

```python
    def _resolve_card(self, data: dict, user_id: int):
        if self.card_repository is None:
            return None
        if data.get("card_id"):
            return self.card_repository.get(data["card_id"], user_id)
        card_label = (data.get("card_label") or "").strip()
        if card_label:
            return self.card_repository.get_by_name(user_id, card_label)
        return None

    def _bill_lookup(self, user_id, card, identifier, year, month):
        if card is not None:
            return self.transaction_repository.get_open_bill_by_card(user_id, card.id, year, month), card
        return self.transaction_repository.get_open_bill(user_id, identifier, year, month), None
```

- Em `_execute_credit` e `_execute_credit_installments`: resolver `card = self._resolve_card(data, user_id)`; usar `card_label = card.name if card else rótulo digitado`; no `due_date` do mês usar `min(card.due_day, último dia)` quando houver cartão, senão dia 1; usar `_bill_lookup`; incluir `"card_id": card.id if card else None` no dict do `transaction_factory.build`.
- Rounding/installments continuam iguais.

- [ ] **Step 3: Rodar testes e commit**

Run: `pytest modules/transactions/tests/test_quick_add_use_case.py -q` — Expected: tudo verde.

```bash
git add backend/modules/transactions/use_cases/transaction/quick_add.py backend/modules/transactions/tests/test_quick_add_use_case.py
git commit -m "feat(transactions): quick add resolves registered cards"
```

### Task 5: Conciliação filtra pelo cartão

**Files:**
- Modify: `backend/modules/transactions/use_cases/transaction/reconcile_bill_preview.py`
- Test: `backend/modules/transactions/tests/test_reconcile_bill_preview_use_case.py`

**Interfaces:**
- Consumes: `TransactionDomain.card_id`.

- [ ] **Step 1: Teste que falha**

Adicionar ao teste existente:

```python
    def test_filters_candidates_by_bill_card(self):
        self.bill.card_id = 3
        other_bill = TransactionDomain(
            id=21, due_date=date(2026, 9, 1), total_amount="50",
            transaction_identifier="Fatura Visa 09/2026", transaction_type="outgoing",
            user_id=7, category="credit_card", card_id=9,
        )
        self.open_bill.card_id = 3
        self.transaction_repository.get_open_bills.return_value = [self.open_bill, other_bill]

        self.use_case.execute(50, user_id=7)

        self.sub_transaction_repository.get_all_by_transaction_ids.assert_called_once_with([20])
```

Run: `pytest modules/transactions/tests/test_reconcile_bill_preview_use_case.py -q` — Expected: FAIL (ids [20, 21]).

- [ ] **Step 2: Implementar**

Em `execute`, após buscar `candidates`:

```python
        bill_card_id = getattr(bill, "card_id", None)
        if bill_card_id is not None:
            candidates = [
                candidate for candidate in candidates
                if getattr(candidate, "card_id", None) == bill_card_id
            ]
```

- [ ] **Step 3: Rodar e commitar**

Run: `pytest modules/transactions/tests/test_reconcile_bill_preview_use_case.py -q` — Expected: verde.

```bash
git add backend/modules/transactions
git commit -m "feat(transactions): reconcile candidates scoped to the bill card"
```

---

## Phase 5 — Upload vinculado ao cartão

### Task 6: `card_id` no upload

**Files:**
- Modify: `backend/modules/file_reader/domains/bill.py`, `factories/bill.py`, `repositories/bill.py`, `use_cases/transpose_file_bill_to_models.py`, `use_cases/upload_file.py`, `views.py`
- Test: `backend/modules/file_reader/tests/test_upload_file_use_case.py`, `backend/modules/file_reader/tests/test_transpose_file_bill_to_models_use_case.py`

**Interfaces:**
- Produces: `UploadFileUseCase.execute(..., card_id=None)`; `TransposeFileBillToModelsUseCase.execute(..., card_id=None)`; fatura importada com `card_id`.

- [ ] **Step 1: Testes que falham**

Em `test_upload_file_use_case.py` (ajustar o teste principal e adicionar um):

```python
    def test_execute_passes_card_id_to_transpose(self):
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "text"
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        mock_ai_call = Mock(spec=AICallDomain)

        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        self.use_case.execute(uploaded_file, user_id, card_id=3)

        self.mock_transpose_use_case.execute.assert_called_once_with("123", user_id, False, card_id=3)
```

Em `test_transpose_file_bill_to_models_use_case.py`:

```python
    def test_sets_card_id_on_created_bill(self):
        mock_file = Mock(spec=FileDomain)
        mock_file.get_response.return_value = {
            "bill_identifier": "Credit Card", "total_amount": 500.00,
            "due_date": "2026-03-15", "transactions": [],
        }
        mock_bill = Mock(spec=BillDomain)
        mock_bill.id = "bill_123"
        self.mock_file_repository.get.return_value = mock_file
        self.mock_bill_factory.build_from_file.return_value = mock_bill
        self.mock_bill_repository.create.return_value = mock_bill
        self.mock_sub_transaction_factory.build_many_from_file.return_value = []

        self.use_case.execute("123", 1, card_id=3)

        self.assertEqual(mock_bill.card_id, 3)
        self.mock_bill_repository.create.assert_called_once_with(mock_bill, 1)
```

Run: `pytest modules/file_reader/tests -q` — Expected: FAIL em ambos.

- [ ] **Step 2: Implementar**

- `domains/bill.py`: parâmetro `card_id: int = None` + `self.card_id = card_id`.
- `factories/bill.py`: `build_from_model` inclui `card_id=model.card_id`; `build_from_other_bill` copia `card_id=bill.card_id`.
- `repositories/bill.py`: `create` inclui `card_id=bill.card_id`.
- `transpose_file_bill_to_models.py`: `execute(self, file_id, user_id, create_in_future_months=False, card_id=None)`; em `_execute_for_one`/`_execute_for_many`, antes do create: `bill.card_id = card_id`.
- `upload_file.py`: `execute(..., card_id=None)`; `transpose.execute(..., card_id=card_id)`.
- `views.py`: `card_id = request.data.get("card_id")`; passar `card_id=card_id`.

- [ ] **Step 3: Rodar e commitar**

Run: `pytest modules/file_reader/tests -q` — Expected: verde.

```bash
git add backend/modules/file_reader
git commit -m "feat(file_reader): link uploaded bill to a card"
```

---

## Phase 6 — Backfill

### Task 7: Migração de dados

**Files:**
- Create: `backend/modules/transactions/services/card_naming.py`, `backend/modules/transactions/tests/test_card_naming.py`, `backend/modules/transactions/migrations/0017_backfill_cards.py`

**Interfaces:**
- Produces: `parse_open_bill_identifier(identifier) -> tuple[str, int, int] | None`.

- [ ] **Step 1: Teste que falha**

`test_card_naming.py`:

```python
from django.test import SimpleTestCase

from modules.transactions.services.card_naming import parse_open_bill_identifier


class TestParseOpenBillIdentifier(SimpleTestCase):
    def test_parses_name_month_year(self):
        self.assertEqual(parse_open_bill_identifier("Fatura Nubank 09/2026"), ("Nubank", 9, 2026))

    def test_parses_multi_word_name(self):
        self.assertEqual(
            parse_open_bill_identifier("Fatura C&A Pay 12/2025"), ("C&A Pay", 12, 2025)
        )

    def test_rejects_other_identifiers(self):
        self.assertIsNone(parse_open_bill_identifier("Nubank"))
        self.assertIsNone(parse_open_bill_identifier("Fatura Nubank"))
```

Run: `pytest modules/transactions/tests/test_card_naming.py -q` — Expected: ImportError.

- [ ] **Step 2: Implementar**

`backend/modules/transactions/services/card_naming.py`:

```python
import re

OPEN_BILL_RE = re.compile(r"^Fatura (.+?) (\d{2})/(\d{4})$")


def parse_open_bill_identifier(identifier: str) -> tuple[str, int, int] | None:
    if not identifier:
        return None
    match = OPEN_BILL_RE.match(identifier.strip())
    if match is None:
        return None
    name, month, year = match.groups()
    return name.strip(), int(month), int(year)
```

- [ ] **Step 3: Migração**

`0017_backfill_cards.py` (depende de `transactions.0016_transaction_card` e `cards.0001_initial`):

```python
from django.db import migrations

from modules.transactions.services.card_naming import parse_open_bill_identifier


def backfill(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    Card = apps.get_model("cards", "Card")

    cards_by_key = {}
    open_bills = Transaction.objects.filter(
        file__isnull=True, category="credit_card", deleted_at__isnull=True
    )
    for bill in open_bills:
        parsed = parse_open_bill_identifier(bill.transaction_identifier)
        if parsed is None:
            continue
        name = parsed[0]
        key = (bill.user_id, name.casefold())
        card = cards_by_key.get(key)
        if card is None:
            card = Card.objects.filter(user_id=bill.user_id, name__iexact=name).first()
        if card is None:
            card = Card.objects.create(name=name, due_day=1, user_id=bill.user_id)
        cards_by_key[key] = card
        bill.card_id = card.id
        bill.save(update_fields=["card"])

    imported_bills = Transaction.objects.filter(
        file__isnull=False, category="credit_card", deleted_at__isnull=True, card__isnull=True
    )
    for bill in imported_bills:
        identifier = (bill.transaction_identifier or "").casefold()
        for card in Card.objects.filter(user_id=bill.user_id):
            if card.name.casefold() in identifier:
                bill.card_id = card.id
                bill.save(update_fields=["card"])
                break


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0001_initial"),
        ("transactions", "0016_transaction_card"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
```

- [ ] **Step 4: Rodar testes e commitar**

Run: `pytest modules/transactions/tests/test_card_naming.py modules/cards/tests -q` — Expected: verde.

```bash
git add backend/modules/transactions
git commit -m "feat(transactions): backfill cards from existing bills"
```

---

## Phase 7 — Frontend

### Task 8: Serviços e tipos

**Files:**
- Create: `frontend/src/services/cards/{getCards,createCard,updateCard,setCardActive}.ts`, `frontend/src/services/transactions/ensureCardBills.ts`
- Modify: `frontend/src/services/types.ts`, `frontend/src/services/index.ts`, `frontend/src/services/bills/uploadBill.ts`

- [ ] **Step 1: Tipos e serviços**

`types.ts` (adicionar):

```typescript
export interface Card {
  id: number;
  name: string;
  due_day: number;
  is_active: boolean;
}

export interface CardInput {
  name: string;
  due_day: number;
}

export interface EnsureCardBillsResult {
  bills: TransactionDetail[];
}
```

Em `Transaction`: adicionar `card_id?: number | null;`.

Serviços (padrão `apiRequest`):

```typescript
// getCards.ts
import { apiRequest } from '../client';
import { Card } from '../types';
export async function getCards(): Promise<Card[]> {
  return apiRequest<Card[]>('/cards/cards/');
}
```

```typescript
// createCard.ts
import { apiRequest } from '../client';
import { Card, CardInput } from '../types';
export async function createCard(data: CardInput): Promise<Card> {
  return apiRequest<Card>('/cards/cards/', { method: 'POST', body: JSON.stringify(data) });
}
```

```typescript
// updateCard.ts
import { apiRequest } from '../client';
import { Card, CardInput } from '../types';
export async function updateCard(id: number, data: Partial<CardInput>): Promise<Card> {
  return apiRequest<Card>(`/cards/cards/${id}/`, { method: 'PATCH', body: JSON.stringify(data) });
}
```

```typescript
// setCardActive.ts
import { apiRequest } from '../client';
import { Card } from '../types';
export async function setCardActive(id: number, isActive: boolean): Promise<Card> {
  return apiRequest<Card>(`/cards/cards/${id}/set_active/`, {
    method: 'POST',
    body: JSON.stringify({ is_active: isActive }),
  });
}
```

```typescript
// ensureCardBills.ts
import { apiRequest } from '../client';
import { TransactionDetail } from '../types';
export async function ensureCardBills(month: string): Promise<TransactionDetail[]> {
  const result = await apiRequest<{ bills: TransactionDetail[] }>(
    '/transactions/transactions/ensure_card_bills/',
    { method: 'POST', body: JSON.stringify({ month }) }
  );
  return result.bills;
}
```

`services/index.ts`: exportar os cinco (e tipos já saem de `types.ts`).

`uploadBill.ts`: assinatura `uploadBill(file, password?, model?, createInFutureMonths?, cardId?)`; no real, `if (cardId) formData.append('card_id', String(cardId));`.

- [ ] **Step 2: Build**

Run: `cd frontend && yarn build` — Expected: verde.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services
git commit -m "feat(fe): cards services and ensure card bills"
```

### Task 9: Seção Cartões em Configurações

**Files:**
- Modify: `frontend/src/app/pages/settings-page.tsx`

- [ ] **Step 1: Implementar**

Adicionar estados e a seção (antes do card de Modo lançamento):

```tsx
const [cards, setCards] = useState<Card[]>([]);
const [showCardForm, setShowCardForm] = useState(false);
const [editingCard, setEditingCard] = useState<Card | null>(null);
const [cardName, setCardName] = useState('');
const [cardDueDay, setCardDueDay] = useState('1');
const [savingCard, setSavingCard] = useState(false);

const loadCards = () => getCards().then(setCards).catch(() => toast.error('Falha ao carregar cartões'));
useEffect(() => { loadCards(); }, []);

const openCardForm = (card?: Card) => {
  setEditingCard(card ?? null);
  setCardName(card?.name ?? '');
  setCardDueDay(String(card?.due_day ?? 1));
  setShowCardForm(true);
};

const handleSaveCard = async (e: React.FormEvent) => {
  e.preventDefault();
  setSavingCard(true);
  try {
    const payload = { name: cardName.trim(), due_day: Math.min(31, Math.max(1, parseInt(cardDueDay, 10) || 1)) };
    if (editingCard) await updateCard(editingCard.id, payload);
    else await createCard(payload);
    setShowCardForm(false);
    loadCards();
    toast.success(editingCard ? 'Cartão atualizado!' : 'Cartão adicionado!');
  } catch {
    toast.error('Falha ao salvar o cartão');
  } finally {
    setSavingCard(false);
  }
};

const handleToggleCard = async (card: Card) => {
  try {
    await setCardActive(card.id, !card.is_active);
    loadCards();
  } catch {
    toast.error('Falha ao atualizar o cartão');
  }
};
```

Card JSX (antes do card de Modo lançamento):

```tsx
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
          <div>
            <CardTitle>Cartões</CardTitle>
            <CardDescription>
              A fatura de cada cartão é criada todo mês, mesmo zerada.
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => openCardForm()} className="shrink-0">
            <Plus className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">Novo cartão</span>
          </Button>
        </CardHeader>
        <CardContent>
          {cards.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">
              Nenhum cartão cadastrado ainda.
            </p>
          ) : (
            <div className="divide-y">
              {cards.map((card) => (
                <div key={card.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-gray-900">{card.name}</span>
                      <Badge variant={card.is_active ? 'default' : 'outline'} className={card.is_active ? '' : 'text-muted-foreground'}>
                        {card.is_active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">vence dia {card.due_day}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline" onClick={() => openCardForm(card)}>
                      Editar
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleToggleCard(card)}>
                      {card.is_active ? 'Desativar' : 'Ativar'}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showCardForm} onOpenChange={setShowCardForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCard ? 'Editar cartão' : 'Novo cartão'}</DialogTitle>
            <DialogDescription>
              O dia de vencimento ancora a fatura do mês no app.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSaveCard}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="card-name">Nome</Label>
                <Input
                  id="card-name"
                  placeholder="Ex: Nubank"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="card-due-day">Dia de vencimento</Label>
                <Input
                  id="card-due-day"
                  type="number"
                  min="1"
                  max="31"
                  inputMode="numeric"
                  value={cardDueDay}
                  onChange={(e) => setCardDueDay(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCardForm(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={savingCard}>
                {savingCard ? 'Salvando...' : 'Salvar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
```

Imports novos no topo do arquivo: `getCards, createCard, updateCard, setCardActive, Card` de `@/services`; `Badge` de `@/app/components/ui/badge`; `Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle` de `@/app/components/ui/dialog`; `Plus` de `lucide-react`.

- [ ] **Step 2: Build e commit**

Run: `cd frontend && yarn build` — Expected: verde.

```bash
git add frontend/src/app/pages/settings-page.tsx
git commit -m "feat(fe): cards crud in settings"
```

### Task 10: Select de cartão no upload

**Files:**
- Modify: `frontend/src/app/components/upload-bill-dialog.tsx`

- [ ] **Step 1: Implementar**

Estados e carregamento:

```tsx
const [cards, setCards] = useState<Card[]>([]);
const [cardId, setCardId] = useState('none');
const [creatingCard, setCreatingCard] = useState(false);
const [newCardName, setNewCardName] = useState('');
const [newCardDueDay, setNewCardDueDay] = useState('1');

useEffect(() => {
  if (!open) return;
  getCards().then(setCards).catch(() => setCards([]));
}, [open]);

useEffect(() => {
  if (!selectedFile || cards.length === 0) return;
  const fileName = selectedFile.name.toLowerCase();
  const match = cards.find((card) => fileName.includes(card.name.toLowerCase()));
  if (match) setCardId(String(match.id));
}, [selectedFile, cards]);

const handleCreateCard = async () => {
  try {
    const created = await createCard({
      name: newCardName.trim(),
      due_day: Math.min(31, Math.max(1, parseInt(newCardDueDay, 10) || 1)),
    });
    setCards((current) => [...current, created]);
    setCardId(String(created.id));
    setCreatingCard(false);
    setNewCardName('');
    toast.success('Cartão adicionado!');
  } catch {
    toast.error('Falha ao criar o cartão');
  }
};
```

JSX (antes do campo de senha/modelo):

```tsx
<div className="space-y-2">
  <Label>Cartão</Label>
  <Select
    value={cardId}
    onValueChange={(value) => {
      if (value === '__new__') {
        setCreatingCard(true);
        setNewCardName(selectedFile?.name?.replace(/\.pdf$/i, '') ?? '');
        setNewCardDueDay('1');
      } else {
        setCardId(value);
      }
    }}
  >
    <SelectTrigger>
      <SelectValue placeholder="Selecione o cartão" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="none">Sem cartão</SelectItem>
      {cards.filter((card) => card.is_active).map((card) => (
        <SelectItem key={card.id} value={String(card.id)}>
          {card.name} (vence dia {card.due_day})
        </SelectItem>
      ))}
      <SelectItem value="__new__">+ novo cartão</SelectItem>
    </SelectContent>
  </Select>
</div>

{creatingCard && (
  <div className="space-y-3 rounded-md border p-3">
    <div className="space-y-2">
      <Label htmlFor="new-card-name">Nome do cartão</Label>
      <Input id="new-card-name" value={newCardName} onChange={(e) => setNewCardName(e.target.value)} />
    </div>
    <div className="space-y-2">
      <Label htmlFor="new-card-due">Dia de vencimento</Label>
      <Input
        id="new-card-due"
        type="number"
        min="1"
        max="31"
        value={newCardDueDay}
        onChange={(e) => setNewCardDueDay(e.target.value)}
      />
    </div>
    <div className="flex justify-end gap-2">
      <Button type="button" variant="ghost" size="sm" onClick={() => setCreatingCard(false)}>
        Cancelar
      </Button>
      <Button type="button" size="sm" onClick={handleCreateCard} disabled={!newCardName.trim()}>
        Criar cartão
      </Button>
    </div>
  </div>
)}
```

Submit:

```tsx
await uploadBill(
  selectedFile,
  password,
  selectedModel,
  createInFutureMonths,
  cardId === 'none' || cardId === '__new__' ? undefined : Number(cardId)
).then((result) => {
```

Imports novos: `getCards, createCard, Card` de `@/services`; `Select, SelectContent, SelectItem, SelectTrigger, SelectValue` já existem no arquivo.

- [ ] **Step 2: Build e commit**

Run: `cd frontend && yarn build` — Expected: verde.

```bash
git add frontend/src/app/components/upload-bill-dialog.tsx
git commit -m "feat(fe): pick the card when uploading a bill"
```

### Task 11: Garantir as faturas ao abrir o mês

**Files:**
- Modify: `frontend/src/app/pages/dashboard-page.tsx`, `frontend/src/app/pages/planning-page.tsx`

- [ ] **Step 1: Implementar**

- Dashboard `loadData`: depois do `ensureSalary`, `await ensureCardBills(selectedMonth).catch(() => undefined);`.
- Planning `load`: idem no `month`.

- [ ] **Step 2: Build, testes e commit**

Run: `cd frontend && yarn build && yarn test` — Expected: verde.

```bash
git add frontend/src/app/pages
git commit -m "feat(fe): ensure card bills when loading a month"
```

---

## Phase 8 — MCP

### Task 12: `card_id` no `create_transaction`

**Files:**
- Modify: `backend/modules/ai/mcp/tools/transactions.py`, `backend/modules/ai/mcp/tools/__init__.py`, `backend/modules/ai/mcp/tests/test_transactions_tools.py`

- [ ] **Step 1: Teste que falha**

```python
    def test_create_routes_card_id_to_quick_add(self):
        quick_add = Mock()
        quick_add.execute.return_value = {"ok": True}
        transactions.call_create_transaction(
            arguments={
                "transaction_identifier": "Padaria",
                "total_amount": "10",
                "due_date": "2026-09-13",
                "payment_method": "credit",
                "card_id": 3,
            },
            use_case=Mock(),
            quick_add_use_case=quick_add,
            user_id=7,
        )
        data = quick_add.execute.call_args[0][0]
        self.assertEqual(data["card_id"], 3)
```

- [ ] **Step 2: Implementar**

- `call_create_transaction`: incluir `"card_id": arguments.get("card_id")` no dict do quick add.
- Schema `create_transaction` em `tools/__init__.py`: propriedade `"card_id": {"type": "integer"}`.
- Descrição: acrescentar "cartão pode ser referenciado por card_id (cadastrado em /cards/) ou card_label".

- [ ] **Step 3: Rodar e commitar**

Run: `pytest modules/ai/mcp/tests/test_transactions_tools.py -q` — Expected: verde.

```bash
git add backend/modules/ai/mcp
git commit -m "feat(mcp): create transaction with registered card"
```

---

## Phase 9 — Verificação final

### Task 13: Fechamento

- [ ] **Step 1: Suítes backend**

Run: `pytest modules/transactions/tests modules/file_reader/tests modules/cards/tests modules/ai/mcp -q`
Expected: verde (exceto as falhas pré-existentes: `test_update_transaction_with_single_sub_transaction`, `TestConnectionsAPI::test_list_connections`, `TestConnectionsAPI::test_revoke_connection`).

- [ ] **Step 2: Frontend**

Run: `cd frontend && yarn build && yarn test`
Expected: verde.

- [ ] **Step 3: Checklist manual**

1. Configurações → criar cartão "Nubank" vencimento 10.
2. Dashboard do mês: "Fatura Nubank MM/AAAA" aparece (zerada) no extrato.
3. Lançar compra de 50 nesse cartão (via MCP com `card_id`) → fatura continua única e total 50.
4. Subir fatura em PDF escolhendo o cartão (sugestão pelo nome do arquivo) → dialog de conciliação pareia só com as compras daquela fatura/cartão.
5. Renomear o cartão em Configurações → fatura do mês mantém o vínculo e o título novo aparece no próximo mês.
6. Desativar o cartão → ensure do mês seguinte não cria fatura dele.

- [ ] **Step 4: Commit final (se houver ajustes)**

```bash
git add -A
git commit -m "chore(cards): final verification adjustments"
```

---

## Ordem sugerida de execução

1. Tasks 1–2 (cartões + FK).
2. Tasks 3–5 (fatura mensal, quick add, conciliação).
3. Task 6–7 (upload + backfill).
4. Tasks 8–11 (frontend).
5. Task 12 (MCP).
6. Task 13 (verificação).
