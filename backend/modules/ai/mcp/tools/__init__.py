"""Adapter layer: defines the MCP tool surface and registers it on a
server instance using the official `mcp` Python SDK.

The HTTP transport in `modules.ai.mcp.http.views` reuses TOOLS and
dispatch_tool so both transports stay in sync.
"""
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from mcp.server import Server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
)

from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.exceptions import MCPError
from modules.ai.mcp.prompts import get_prompt as build_prompt
from modules.ai.mcp.prompts import list_prompts
from modules.ai.mcp.tools import sub_transactions
from modules.ai.mcp.tools import transactions
from modules.ai.mcp.tools.list_enums import (
    LIST_ENUMS_DESCRIPTION,
    call_list_enums,
)


logger = logging.getLogger("modules.ai.mcp")


def dumps_payload(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, cls=DjangoJSONEncoder)


TOOLS = [
    {
        "name": "list_transactions",
        "description": transactions.LIST_TRANSACTIONS_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "due_start": {"type": "string", "description": "Vencimento a partir de (YYYY-MM-DD)"},
                "due_end": {"type": "string", "description": "Vencimento até (YYYY-MM-DD)"},
                "due_month": {"type": "string", "description": "Mês do vencimento/fatura (YYYY-MM)"},
                "include_subtransactions": {"type": "boolean", "description": "Inclui as compras (subtransações) de cada transação"},
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
                "card_id": {"type": "integer"},
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
    {
        "name": "get_projection",
        "description": transactions.GET_PROJECTION_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "YYYY-MM"},
                "end": {"type": "string", "description": "YYYY-MM"},
                "months": {"type": "integer", "minimum": 1, "maximum": 24},
            },
        },
    },
    {
        "name": "set_goals",
        "description": transactions.SET_GOALS_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                  "spending_goal_percent": {"type": "number", "minimum": 0, "maximum": 100, "description": "Teto de gasto em % da renda"},
                  "savings_goal_percent": {"type": "number", "minimum": 0, "maximum": 100, "description": "Quanto guardar em % da renda"},
                  "essentials_goal_percent": {"type": "number", "minimum": 0, "maximum": 100, "description": "Teto de gastos essenciais em % da renda"},
            },
        },
    },
    {
        "name": "list_sub_transactions",
        "description": sub_transactions.LIST_SUB_TRANSACTIONS_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "purchase_month": {"type": "string", "description": "Mês da compra (YYYY-MM)"},
                "purchase_start": {"type": "string", "description": "Compra a partir de (YYYY-MM-DD)"},
                "purchase_end": {"type": "string", "description": "Compra até (YYYY-MM-DD)"},
                "due_month": {"type": "string", "description": "Mês do vencimento da fatura pai (YYYY-MM)"},
                "due_start": {"type": "string", "description": "Vencimento a partir de (YYYY-MM-DD)"},
                "due_end": {"type": "string", "description": "Vencimento até (YYYY-MM-DD)"},
                "category": {"type": "string"},
                "search": {"type": "string", "description": "Trecho da descrição da compra"},
                "transaction_id": {"type": "integer"},
                "actor_id": {"type": "integer"},
                "limit": {"type": "integer", "maximum": 200},
            },
        },
    },
]


HANDLERS = {
    "list_transactions": lambda arguments, container, user_id: transactions.call_list_transactions(
        arguments=arguments,
        use_case=container.transactions_container().list_transactions_use_case(),
        user_id=user_id,
    ),
    "get_transaction": lambda arguments, container, user_id: transactions.call_get_transaction(
        arguments=arguments,
        use_case=container.transactions_container().get_transaction_use_case(),
        user_id=user_id,
    ),
    "create_transaction": lambda arguments, container, user_id: transactions.call_create_transaction(
        arguments=arguments,
        use_case=container.transactions_container().create_transaction_use_case(),
        quick_add_use_case=container.transactions_container().quick_add_transaction_use_case(),
        user_id=user_id,
    ),
    "update_transaction": lambda arguments, container, user_id: transactions.call_update_transaction(
        arguments=arguments,
        use_case=container.transactions_container().update_transaction_use_case(),
        user_id=user_id,
    ),
    "create_sub_transaction": lambda arguments, container, user_id: transactions.call_create_sub_transaction(
        arguments=arguments,
        use_case=container.transactions_container().create_sub_transaction_use_case(),
        user_id=user_id,
    ),
    "update_sub_transaction": lambda arguments, container, user_id: transactions.call_update_sub_transaction(
        arguments=arguments,
        use_case=container.transactions_container().update_sub_transaction_use_case(),
        user_id=user_id,
    ),
    "list_enums": lambda arguments, container, user_id: call_list_enums(
        use_case=container.list_enums_use_case(),
    ),
    "get_projection": lambda arguments, container, user_id: transactions.call_get_projection(
        arguments=arguments,
        use_case=container.planning_container().projection_use_case(),
        user_id=user_id,
    ),
    "set_goals": lambda arguments, container, user_id: transactions.call_set_goals(
        arguments=arguments,
        update_profile_use_case=container.userdata_container().update_profile_use_case(),
        profile_repository=container.planning_container().profile_repository(),
        user_id=user_id,
    ),
    "list_sub_transactions": lambda arguments, container, user_id: sub_transactions.call_list_sub_transactions(
        arguments=arguments,
        use_case=container.transactions_container().list_sub_transactions_use_case(),
        user_id=user_id,
    ),
}


def dispatch_tool(name: str, arguments: dict, container: MCPContainer, user_id: int) -> dict:
    handler = HANDLERS.get(name)
    if handler is None:
        return {
            "error": {
                "code": "UNKNOWN_TOOL",
                "message": f"unknown tool: {name}",
                "available_tools": sorted(HANDLERS),
            }
        }
    try:
        return handler(arguments=arguments, container=container, user_id=user_id)
    except MCPError as exc:
        return {"error": {"code": exc.code, "message": str(exc)}}
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
        return [TextContent(type="text", text=dumps_payload(payload))]

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name=prompt["name"],
                description=prompt["description"],
                arguments=[PromptArgument(**argument) for argument in prompt["arguments"]],
            )
            for prompt in list_prompts()
        ]

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        payload = build_prompt(name, arguments)
        if payload is None:
            raise ValueError(f"prompt não encontrado: {name!r}")
        return GetPromptResult(
            description=payload["description"],
            messages=[
                PromptMessage(
                    role=message["role"],
                    content=TextContent(type="text", text=message["content"]["text"]),
                )
                for message in payload["messages"]
            ],
        )
