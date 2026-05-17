from modules.ai.mcp.factories.enum_listing import EnumListingFactory
from modules.transactions.models import Transaction
from modules.transactions.types import TransactionCategory


class ListEnumsUseCase:
    def __init__(self, enum_listing_factory: EnumListingFactory):
        self.enum_listing_factory = enum_listing_factory

    def execute(self) -> dict:
        category = self.enum_listing_factory.from_basetype(
            "TransactionCategory", TransactionCategory
        )
        tx_type = self.enum_listing_factory.from_choices(
            "TransactionType",
            list(Transaction.TransactionType.choices),
        )
        out: dict = {}
        out.update(category.to_dict())
        out.update(tx_type.to_dict())
        return out
