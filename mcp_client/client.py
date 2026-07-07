"""
mcp_client/client.py
====================
Synchronous MCP client that connects to mcp_server/server.py via stdio.

Usage (singleton pattern):
    from mcp_client.client import get_client
    result = get_client().call_tool("get_weather", {"city": "Goa"})

The client is created once per process and reused for every tool call.
"""

import json
import subprocess
import sys
import os


class MCPClient:
    """
    Lightweight synchronous MCP client.
    Spawns the MCP server as a subprocess and communicates over stdin/stdout
    using the JSON-RPC 2.0 protocol that MCP is built on.
    """

    def __init__(self):
        self._process = None
        self._msg_id = 0
        self._initialized = False

    # ──────────────────────────────────────────────────────────────
    # Process lifecycle
    # ──────────────────────────────────────────────────────────────

    def _start(self):
        """Spawn the MCP server subprocess."""

        server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mcp_server",
            "server.py"
        )

        self._process = subprocess.Popen(
            [sys.executable, "-X", "utf8", server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        self._initialize()

    def _initialize(self):
        """Send MCP initialize + initialized handshake."""

        self._send({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "trip-planner-client",
                    "version": "1.0"
                },
            },
        })

        self._read_response()

        self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        })

        self._initialized = True

    def _ensure_started(self):
        if self._process is None or self._process.poll() is not None:
            self._initialized = False
            self._start()

    # ──────────────────────────────────────────────────────────────
    # JSON-RPC Helpers
    # ──────────────────────────────────────────────────────────────

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    def _send(self, payload: dict):
        line = json.dumps(payload) + "\n"

        self._process.stdin.write(line)
        self._process.stdin.flush()

    def _read_response(self) -> dict:
        """Read one JSON response from the MCP server."""

        try:
            line = self._process.stdout.readline()

            if not line:

                stderr_output = ""

                try:
                    if self._process.stderr:
                        stderr_output = self._process.stderr.read()
                except Exception:
                    pass

                raise RuntimeError(
                    f"MCP server closed unexpectedly.\n\nSTDERR:\n{stderr_output}"
                )

            line = line.strip()

            if not line:
                raise RuntimeError("Received empty response from MCP server.")

            return json.loads(line)

        except UnicodeDecodeError as e:
            raise RuntimeError(
                f"UnicodeDecodeError while reading MCP response:\n{e}"
            )

        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Invalid JSON received from MCP server.\n\n"
                f"Response:\n{line}\n\n"
                f"Error:\n{e}"
            )

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    def call_tool(self, tool_name: str, arguments: dict):
        """
        Call a tool exposed by the MCP server.

        Returns:
            Parsed Python object if JSON.
            Raw string otherwise.
        """

        self._ensure_started()

        msg_id = self._next_id()

        self._send({
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        })

        response = self._read_response()

        if "error" in response:
            return {
                "error": response["error"].get(
                    "message",
                    "Unknown MCP error"
                )
            }

        result = response.get("result", {})
        contents = result.get("content", [])

        if not contents:
            return {"error": "Empty response from MCP server"}

        raw_text = contents[0].get("text", "")

        try:
            return json.loads(raw_text)

        except (json.JSONDecodeError, TypeError):
            return raw_text

    def list_tools(self) -> list:
        """Return all registered MCP tool names."""

        self._ensure_started()

        msg_id = self._next_id()

        self._send({
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": "tools/list",
            "params": {},
        })

        response = self._read_response()

        tools = response.get("result", {}).get("tools", [])

        return [tool["name"] for tool in tools]

    def close(self):
        """Terminate MCP server."""

        if self._process and self._process.poll() is None:
            self._process.terminate()

        self._process = None


# ──────────────────────────────────────────────────────────────
# Singleton
# ──────────────────────────────────────────────────────────────

_client_instance = None


def get_client() -> MCPClient:
    """Return shared MCP client instance."""

    global _client_instance

    if _client_instance is None:
        _client_instance = MCPClient()

    return _client_instance
# """
# mcp_client/client.py
# ====================
# Synchronous MCP client that connects to mcp_server/server.py via stdio.

# Usage (singleton pattern):
#     from mcp_client.client import get_client
#     result = get_client().call_tool("get_weather", {"city": "Goa"})

# The client is created once per process and reused for every tool call.
# """

# import json
# import subprocess
# import sys
# import os


# class MCPClient:
#     """
#     Lightweight synchronous MCP client.
#     Spawns the MCP server as a subprocess and communicates over stdin/stdout
#     using the JSON-RPC 2.0 protocol that MCP is built on.
#     """

#     def __init__(self):
#         self._process  = None
#         self._msg_id   = 0
#         self._initialized = False

#     # ── Process lifecycle ─────────────────────────────────────────────────────

#     def _start(self):
#         """Spawn the MCP server subprocess."""
#         server_path = os.path.join(
#             os.path.dirname(os.path.dirname(__file__)),
#             "mcp_server", "server.py"
#         )
#         self._process = subprocess.Popen(
#             [sys.executable, server_path],
#             stdin  = subprocess.PIPE,
#             stdout = subprocess.PIPE,
#             stderr = subprocess.PIPE,
#             text   = True,
#             bufsize= 1,
#         )
#         self._initialize()

#     def _initialize(self):
#         """Send MCP initialize + initialized handshake."""
#         # initialize request
#         self._send({
#             "jsonrpc": "2.0",
#             "id":      self._next_id(),
#             "method":  "initialize",
#             "params":  {
#                 "protocolVersion": "2024-11-05",
#                 "capabilities":    {},
#                 "clientInfo":      {"name": "trip-planner-client", "version": "1.0"},
#             },
#         })
#         self._read_response()   # consume initialize response

#         # initialized notification (no response expected)
#         self._send({
#             "jsonrpc": "2.0",
#             "method":  "notifications/initialized",
#             "params":  {},
#         })
#         self._initialized = True

#     def _ensure_started(self):
#         if self._process is None or self._process.poll() is not None:
#             self._initialized = False
#             self._start()

#     # ── Low-level JSON-RPC helpers ────────────────────────────────────────────

#     def _next_id(self) -> int:
#         self._msg_id += 1
#         return self._msg_id

#     def _send(self, payload: dict):
#         line = json.dumps(payload) + "\n"
#         self._process.stdin.write(line)
#         self._process.stdin.flush()

#     def _read_response(self) -> dict:
#         """Read one JSON line from the server stdout."""
#         line = self._process.stdout.readline()
#         if not line:
#             raise RuntimeError("MCP server closed unexpectedly.")
#         return json.loads(line.strip())

#     # ── Public API ────────────────────────────────────────────────────────────

#     def call_tool(self, tool_name: str, arguments: dict):
#         """
#         Call an MCP tool and return the parsed result.

#         Returns:
#             Parsed Python object (dict / list) if the response is JSON,
#             otherwise the raw string text.
#         """
#         self._ensure_started()

#         msg_id = self._next_id()
#         self._send({
#             "jsonrpc": "2.0",
#             "id":      msg_id,
#             "method":  "tools/call",
#             "params":  {
#                 "name":      tool_name,
#                 "arguments": arguments,
#             },
#         })

#         response = self._read_response()

#         # Handle JSON-RPC error
#         if "error" in response:
#             return {"error": response["error"].get("message", "Unknown MCP error")}

#         # Extract content from result
#         result   = response.get("result", {})
#         contents = result.get("content", [])

#         if not contents:
#             return {"error": "Empty response from MCP server"}

#         raw_text = contents[0].get("text", "")

#         # Try to parse as JSON; return raw string if not parseable
#         try:
#             return json.loads(raw_text)
#         except (json.JSONDecodeError, TypeError):
#             return raw_text

#     def list_tools(self) -> list:
#         """Return the list of tool names registered on the server."""
#         self._ensure_started()
#         msg_id = self._next_id()
#         self._send({
#             "jsonrpc": "2.0",
#             "id":      msg_id,
#             "method":  "tools/list",
#             "params":  {},
#         })
#         response = self._read_response()
#         tools    = response.get("result", {}).get("tools", [])
#         return [t["name"] for t in tools]

#     def close(self):
#         """Terminate the server subprocess."""
#         if self._process and self._process.poll() is None:
#             self._process.terminate()
#             self._process = None


# # ── Singleton ─────────────────────────────────────────────────────────────────

# _client_instance: MCPClient = None


# def get_client() -> MCPClient:
#     """Return the shared MCPClient instance (create on first call)."""
#     global _client_instance
#     if _client_instance is None:
#         _client_instance = MCPClient()
#     return _client_instance
