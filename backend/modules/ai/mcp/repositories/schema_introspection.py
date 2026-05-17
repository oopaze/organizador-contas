from typing import Type

from django.apps import apps
from django.db import models

from modules.ai.mcp.domains.table_schema import TableSchema
from modules.ai.mcp.exceptions import SchemaIntrospectionError
from modules.ai.mcp.factories.table_schema import TableSchemaFactory
from modules.ai.mcp.schema_docs import SCOPED_TABLES


class SchemaIntrospectionRepository:
    def __init__(self, table_schema_factory: TableSchemaFactory):
        self.table_schema_factory = table_schema_factory

    def list_all(self) -> list[TableSchema]:
        return [
            self.table_schema_factory.from_django_model(model)
            for model in self._models_for_scoped_tables()
        ]

    def get(self, table_name: str) -> TableSchema:
        if table_name not in SCOPED_TABLES:
            raise SchemaIntrospectionError(
                f"table {table_name!r} is not exposed via MCP"
            )
        for model in self._models_for_scoped_tables():
            if model._meta.db_table == table_name:
                return self.table_schema_factory.from_django_model(model)
        raise SchemaIntrospectionError(
            f"table {table_name!r} not found in Django app registry"
        )

    def _models_for_scoped_tables(self) -> list[Type[models.Model]]:
        out = []
        scoped = set(SCOPED_TABLES)
        for model in apps.get_models():
            if model._meta.db_table in scoped:
                out.append(model)
        if len(out) != len(scoped):
            missing = scoped - {m._meta.db_table for m in out}
            raise SchemaIntrospectionError(
                f"scoped tables missing from app registry: {sorted(missing)}"
            )
        return out
