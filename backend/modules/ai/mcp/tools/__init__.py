"""Adapter layer: registers MCP tools on a server instance using the
official `mcp` Python SDK. Each tool delegates to a use case from the
MCPContainer.
"""
import json
from typing import Optional

from mcp.server import Server
from mcp.types import TextContent, Tool

from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.tools.describe_schema import (
    DESCRIBE_SCHEMA_DESCRIPTION,
    call_describe_schema,
)
from modules.ai.mcp.tools.execute_sql import (
    EXECUTE_SQL_DESCRIPTION,
    call_execute_sql,
)
from modules.ai.mcp.tools.list_enums import (
    LIST_ENUMS_DESCRIPTION,
    call_list_enums,
)


def register_tools(server: Server, container: MCPContainer, user_id: int) -> None:
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="execute_sql",
                description=EXECUTE_SQL_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SELECT or WITH ... SELECT statement.",
                        }
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="describe_schema",
                description=DESCRIBE_SCHEMA_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": (
                                "Optional table name. If omitted, returns "
                                "all scoped tables."
                            ),
                        }
                    },
                },
            ),
            Tool(
                name="list_enums",
                description=LIST_ENUMS_DESCRIPTION,
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "execute_sql":
            payload = call_execute_sql(
                query=arguments["query"],
                use_case=container.execute_sql_use_case(),
                user_id=user_id,
            )
        elif name == "describe_schema":
            payload = call_describe_schema(
                table=arguments.get("table"),
                use_case=container.describe_schema_use_case(),
            )
        elif name == "list_enums":
            payload = call_list_enums(
                use_case=container.list_enums_use_case(),
            )
        else:
            payload = {
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": f"unknown tool: {name}",
                }
            }
        return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
