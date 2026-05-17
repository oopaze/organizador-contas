from typing import Type

from django.db import models

from modules.ai.mcp.domains.table_schema import ColumnSchema, TableSchema
from modules.ai.mcp.schema_docs import COLUMN_NOTES, TABLE_DESCRIPTIONS


CATEGORY_FIELDS = {"category"}  # columns backed by TransactionCategory enum


class TableSchemaFactory:
    def from_django_model(self, model: Type[models.Model]) -> TableSchema:
        meta = model._meta
        table = meta.db_table
        description = TABLE_DESCRIPTIONS.get(table, "")

        indexed_columns = self._indexed_columns(meta)
        columns: list[ColumnSchema] = []
        for field in meta.get_fields():
            if not getattr(field, "concrete", False):
                continue
            if getattr(field, "many_to_many", False):
                continue
            col_name = field.column if hasattr(field, "column") else field.name
            columns.append(
                ColumnSchema(
                    name=col_name,
                    type=self._field_type(field),
                    pk=bool(getattr(field, "primary_key", False)),
                    indexed=col_name in indexed_columns,
                    nullable=bool(getattr(field, "null", False)),
                    enum=self._enum_choices(field),
                    enum_ref=(
                        "TransactionCategory"
                        if col_name in CATEGORY_FIELDS
                        else None
                    ),
                    fk=self._fk(field),
                    notes=COLUMN_NOTES.get((table, col_name)),
                )
            )

        relationships = self._relationships(model)
        return TableSchema(
            name=table,
            description=description,
            columns=columns,
            relationships=relationships,
        )

    def _field_type(self, field) -> str:
        internal = field.get_internal_type()
        mapping = {
            "BigAutoField": "bigint",
            "AutoField": "integer",
            "CharField": "varchar",
            "TextField": "text",
            "DateField": "date",
            "DateTimeField": "timestamptz",
            "DecimalField": (
                f"numeric({getattr(field, 'max_digits', '')},"
                f"{getattr(field, 'decimal_places', '')})"
            ),
            "BooleanField": "boolean",
            "IntegerField": "integer",
            "BigIntegerField": "bigint",
            "ForeignKey": "bigint",
            "OneToOneField": "bigint",
            "FileField": "varchar",
        }
        return mapping.get(internal, internal.lower())

    def _enum_choices(self, field) -> list[str] | None:
        choices = getattr(field, "choices", None)
        if not choices:
            return None
        if field.column == "category":
            return None
        return [str(value) for value, _ in choices]

    def _fk(self, field) -> str | None:
        if not field.is_relation or not field.many_to_one:
            return None
        related = field.related_model
        return f"{related._meta.db_table}.{related._meta.pk.column}"

    def _indexed_columns(self, meta) -> set[str]:
        indexed = set()
        for index in meta.indexes:
            for field_name in index.fields:
                indexed.add(
                    meta.get_field(field_name).column
                )
        for field in meta.get_fields():
            if getattr(field, "db_index", False):
                indexed.add(field.column)
            if getattr(field, "primary_key", False):
                indexed.add(field.column)
        return indexed

    def _relationships(self, model) -> list[str]:
        rels = []
        meta = model._meta
        for field in meta.get_fields():
            if field.one_to_many:
                target = field.related_model._meta.db_table
                rels.append(
                    f"has many {target} (via {field.field.column})"
                )
            elif field.many_to_one:
                target = field.related_model._meta.db_table
                col = field.column
                rels.append(f"references {target} (via {col})")
        return rels
