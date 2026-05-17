"""End-to-end smoke test of the MCP server over stdio.

Spawns `python manage.py run_mcp` as a subprocess, sends MCP JSON-RPC
init + list_tools, and asserts the three expected tools are advertised.

Enable with environment variable: MCP_SMOKE_TEST=1
"""
import os

import pytest


if os.environ.get("MCP_SMOKE_TEST") != "1":
    pytest.skip(
        "Set MCP_SMOKE_TEST=1 to run the server smoke test "
        "(requires real DB and poupix_mcp_ro role).",
        allow_module_level=True,
    )


import json
import subprocess
import sys
import time
import unittest


class TestServerSmoke(unittest.TestCase):
    def test_list_tools_returns_three(self):
        env = os.environ.copy()
        env["POUPIX_MCP_USER_ID"] = env.get("POUPIX_MCP_USER_ID", "1")

        proc = subprocess.Popen(
            [sys.executable, "manage.py", "run_mcp"],
            cwd="backend",
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        try:
            init = {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "smoke", "version": "0"},
                },
            }
            proc.stdin.write(json.dumps(init) + "\n")
            proc.stdin.flush()

            initd = {"jsonrpc": "2.0", "method": "notifications/initialized"}
            proc.stdin.write(json.dumps(initd) + "\n")
            proc.stdin.flush()

            req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()

            deadline = time.monotonic() + 8
            tool_names: list[str] = []
            while time.monotonic() < deadline:
                line = proc.stdout.readline()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if msg.get("id") == 2 and "result" in msg:
                    tool_names = [t["name"] for t in msg["result"]["tools"]]
                    break

            self.assertEqual(
                sorted(tool_names),
                sorted(["execute_sql", "describe_schema", "list_enums"]),
            )
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
