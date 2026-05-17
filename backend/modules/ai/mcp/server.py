import asyncio
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server

from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.tools import register_tools


def _resolve_user_id() -> int:
    raw = os.environ.get("POUPIX_MCP_USER_ID")
    if not raw:
        raise SystemExit(
            "POUPIX_MCP_USER_ID is required. Set it in your MCP client's "
            "configuration (e.g. mcp.json) to the user id whose data the "
            "agent should access."
        )
    try:
        return int(raw)
    except ValueError as exc:
        raise SystemExit(
            f"POUPIX_MCP_USER_ID must be an integer (got: {raw!r})"
        ) from exc


async def _amain() -> None:
    user_id = _resolve_user_id()
    container = MCPContainer()
    server = Server("poupix-mcp")
    register_tools(server, container, user_id=user_id)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run() -> None:
    asyncio.run(_amain())
