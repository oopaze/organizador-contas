"""Adapter layer: defines the MCP tool surface and registers it on a
server instance using the official `mcp` Python SDK.

The HTTP transport in `modules.ai.mcp.http.views` reuses TOOLS and
dispatch_tool so both transports stay in sync.
"""
import json
import logging

from mcp.server import Server
from mcp.types import TextContent, Tool

from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.tools import transactions
from modules.ai.mcp.tools.list_enums import (
    LIST_ENUMS_DESCRIPTION,
    call_list_enums,
)


logger = logging.getLogger("modules.ai.mcp")


TOOLS = [
    {
        "name": "list_transactions",
        "description": transactions.LIST_TRANSACTIONS_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "YYYY-MM-DD"},
                "end": {"type": "string", "description": "YYYY-MM-DD"},
                "month": {"type": "string", "description": "YYYY-MM"},
                "transaction_type": {"type": "string", "enum": ["incoming", "outgoing"]},
                "category": {"type": "string"},
                "paid": {"type": "boolean"},
                "search": {"type": "string"},
                "limit": {"type": "integer", "maximum": 200},
            },
        },
    },
    {
        "name": "get_transaction",
        "description": transactions.GET_TRANSACTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {"transaction_id": {"type": "integer"}},
            "required": ["transaction_id"],
        },
    },
    {
        "name": "create_transaction",
        "description": transactions.CREATE_TRANSACTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "transaction_identifier": {"type": "string"},
                "total_amount": {"type": "string"},
                "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                "transaction_type": {"type": "string", "enum": ["incoming", "outgoing"]},
                "payment_method": {"type": "string", "enum": ["cash", "credit"]},
                "card_label": {"type": "string"},
                "installments": {"type": "integer", "minimum": 1},
                "category": {"type": "string"},
                "is_salary": {"type": "boolean"},
                "is_recurrent": {"type": "boolean"},
                "recurrence_count": {"type": "integer"},
                "is_paid": {"type": "boolean"},
                "paid_at": {"type": "string", "description": "YYYY-MM-DD"},
                "actor_id": {"type": "integer"},
            },
            "required": ["transaction_identifier", "total_amount", "due_date"],
        },
    },
    {
        "name": "update_transaction",
        "description": transactions.UPDATE_TRANSACTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "integer"},
                "transaction_identifier": {"type": "string"},
                "total_amount": {"type": "string"},
                "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                "transaction_type": {"type": "string", "enum": ["incoming", "outgoing"]},
                "category": {"type": "string"},
                "is_salary": {"type": "boolean"},
            },
            "required": ["transaction_id"],
        },
    },
    {
        "name": "create_sub_transaction",
        "description": transactions.CREATE_SUB_TRANSACTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "integer"},
                "description": {"type": "string"},
                "amount": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "category": {"type": "string"},
                "installment_info": {"type": "string", "description": "ex: 1/3"},
                "paid_at": {"type": "string", "description": "YYYY-MM-DD"},
                "actor_id": {"type": "integer"},
            },
            "required": ["transaction_id", "description", "amount"],
        },
    },
    {
        "name": "update_sub_transaction",
        "description": transactions.UPDATE_SUB_TRANSACTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "sub_transaction_id": {"type": "integer"},
                "description": {"type": "string"},
                "amount": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "category": {"type": "string"},
                "installment_info": {"type": "string"},
                "user_provided_description": {"type": "string"},
                "actor": {"type": ["integer", "null"]},
            },
            "required": ["sub_transaction_id"],
        },
    },
    {
        "name": "list_enums",
        "description": LIST_ENUMS_DESCRIPTION,
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def dispatch_tool(name: str, arguments: dict, container: MCPContainer, user_id: int) -> dict:
    try:
        transactions_container = container.transactions_container()
        if name == "list_transactions":
            return transactions.call_list_transactions(
                arguments=arguments,
                use_case=transactions_container.list_transactions_use_case(),
                user_id=user_id,
            )
        if name == "get_transaction":
            return transactions.call_get_transaction(
                arguments=arguments,
                use_case=transactions_container.get_transaction_use_case(),
                user_id=user_id,
            )
        if name == "create_transaction":
            return transactions.call_create_transaction(
                arguments=arguments,
                use_case=transactions_container.create_transaction_use_case(),
                quick_add_use_case=transactions_container.quick_add_transaction_use_case(),
                user_id=user_id,
            )
        if name == "update_transaction":
            return transactions.call_update_transaction(
                arguments=arguments,
                use_case=transactions_container.update_transaction_use_case(),
                user_id=user_id,
            )
        if name == "create_sub_transaction":
            return transactions.call_create_sub_transaction(
                arguments=arguments,
                use_case=transactions_container.create_sub_transaction_use_case(),
                user_id=user_id,
            )
        if name == "update_sub_transaction":
            return transactions.call_update_sub_transaction(
                arguments=arguments,
                use_case=transactions_container.update_sub_transaction_use_case(),
                user_id=user_id,
            )
        if name == "list_enums":
            return call_list_enums(use_case=container.list_enums_use_case())
        return {
            "error": {
                "code": "UNKNOWN_TOOL",
                "message": f"unknown tool: {name}",
            }
        }
    except Exception as exc:  # noqa: BLE001 - surfaced to the agent as tool error
        logger.info("mcp.tool_error tool=%s error=%s", name, exc)
        return {"error": {"code": "TOOL_ERROR", "message": str(exc)}}


def register_tools(server: Server, container: MCPContainer, user_id: int) -> None:
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["inputSchema"],
            )
            for tool in TOOLS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        payload = dispatch_tool(name, arguments, container, user_id)
        return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
