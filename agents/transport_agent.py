"""
agents/transport_agent.py
Calls MCP TOOL 2 (web_search) twice via mcp_client/tools.py —
once for how to reach, once for local transport.
"""

from mcp_client.tools import search_serper
from services.llm import call_gemini


def _snippets(result: dict, n: int = 3) -> str:
    if not isinstance(result, dict) or "error" in result:
        return "- Live data not available.\n"
    return "".join(
        f"- {r.get('title','')}: {r.get('snippet','')}\n"
        for r in (result.get("organic") or [])[:n]
    ) or "- No results.\n"


def transport_agent(state: dict) -> dict:
    print("running transport agent  →  MCP TOOL 2: web_search (Serper)")

    place    = state.get("trip_place", "")
    warnings = state.setdefault("warnings", [])
    trace    = state.setdefault("trace", [])

    if not place:
        state["transport_info"] = "Transport details not available — destination missing."
        state["warnings"] = warnings
        return state

    # ── MCP TOOL 2 — how to reach ─────────────────────────────────────────────
    reach = search_serper(query=f"how to reach {place} by flight train bus", num_results=3)

    # ── MCP TOOL 2 — local transport ─────────────────────────────────────────
    local = search_serper(query=f"local transport options for tourists in {place}", num_results=3)

    transport_info = (
        f"Getting to {place}:\n{_snippets(reach)}\n"
        f"Getting around {place}:\n{_snippets(local)}"
    ).strip()

    state["transport_info"] = transport_info
    trace.append({
        "step":   "Transport",
        "source": "MCP TOOL 2: web_search x2 (Serper)",
        "output": transport_info[:300],
    })
    state["warnings"] = warnings
    return state
