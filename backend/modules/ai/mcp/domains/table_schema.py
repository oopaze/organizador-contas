from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ColumnSchema:
    name: str
    type: str
    pk: bool = False
    indexed: bool = False
    nullable: bool = True
    enum: Optional[list[str]] = None
    enum_ref: Optional[str] = None
    fk: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class TableSchema:
    name: str
    description: str
    columns: list[ColumnSchema]
    relationships: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "columns": [
                {k: v for k, v in vars(c).items() if v is not None and v is not False}
                for c in self.columns
            ],
            "relationships": list(self.relationships),
        }
