from typing import Type

from modules.ai.mcp.domains.enum_listing import EnumListing, EnumValue
from modules.base.types import BaseType, TypeItem


class EnumListingFactory:
    def from_basetype(self, name: str, base_type: Type[BaseType]) -> EnumListing:
        values: list[EnumValue] = []
        for item in base_type.get_all():
            # TypeItem uses .name as the identifier key and .value as the label
            slug = item.name
            label = getattr(item, "value", item.name)
            values.append(EnumValue(slug=str(slug), label=str(label)))
        return EnumListing(name=name, values=values)

    def from_choices(self, name: str, choices: list[tuple[str, str]]) -> EnumListing:
        return EnumListing(
            name=name,
            values=[EnumValue(slug=slug, label=label) for slug, label in choices],
        )
