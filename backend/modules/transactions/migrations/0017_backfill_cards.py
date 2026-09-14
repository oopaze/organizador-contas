from django.db import migrations

from modules.transactions.services.card_naming import parse_open_bill_identifier


def backfill(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    Card = apps.get_model("cards", "Card")

    cards_by_key = {}
    open_bills = Transaction.objects.filter(
        file__isnull=True,
        category="credit_card",
        deleted_at__isnull=True,
        card__isnull=True,
    )
    for bill in open_bills:
        parsed = parse_open_bill_identifier(bill.transaction_identifier)
        if parsed is None:
            continue
        name = parsed[0]
        if not name:
            continue
        key = (bill.user_id, name.casefold())
        card = cards_by_key.get(key)
        if card is None:
            card = Card.objects.filter(
                user_id=bill.user_id, name__iexact=name, deleted_at__isnull=True
            ).first()
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
        card = max(
            (
                candidate
                for candidate in Card.objects.filter(
                    user_id=bill.user_id, deleted_at__isnull=True
                )
                if candidate.name.casefold() in identifier
            ),
            key=lambda candidate: len(candidate.name),
            default=None,
        )
        if card is not None:
            bill.card_id = card.id
            bill.save(update_fields=["card"])


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0001_initial"),
        ("transactions", "0016_transaction_card"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
