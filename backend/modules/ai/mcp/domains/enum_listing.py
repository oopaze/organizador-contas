from dataclasses import dataclass


@dataclass(frozen=True)
class EnumValue:
    slug: str
    label: str


@dataclass(frozen=True)
class EnumListing:
    name: str
    values: list[EnumValue]

    def to_dict(self) -> dict:
        return {
            self.name: [
                {"slug": v.slug, "label": v.label} for v in self.values
            ]
        }
