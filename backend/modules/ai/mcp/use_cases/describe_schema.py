from typing import Optional

from modules.ai.mcp.repositories.schema_introspection import (
    SchemaIntrospectionRepository,
)


class DescribeSchemaUseCase:
    def __init__(
        self,
        schema_introspection_repository: SchemaIntrospectionRepository,
    ):
        self.schema_introspection_repository = schema_introspection_repository

    def execute(self, *, table: Optional[str]) -> dict:
        if table:
            return self.schema_introspection_repository.get(table).to_dict()
        return {
            "tables": [
                t.to_dict()
                for t in self.schema_introspection_repository.list_all()
            ]
        }
