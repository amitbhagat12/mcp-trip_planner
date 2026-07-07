"""
agents/budget_agent.py
Calls MCP TOOL 2 (web_search) 3 times for live cost data,
then uses Gemini to produce a structured JSON budget estimate.
"""

from mcp_client.tools import search_serper
from services.llm import call_gemini, extract_json


def _titles(result: dict, n: int = 3) -> str:
    if not isinstance(result, dict) or "error" in result:
        return ""
    return "\n".join(
        f"- {r.get('title','')}: {r.get('snippet','')}"
        for r in (result.get("organic") or [])[:n]
    )


def budget_agent(state: dict) -> dict:
    print("running budget agent  →  MCP TOOL 2: web_search x3 (Serper) + Gemini")

    place    = state.get("trip_place", "")
    days     = state.get("trip_days", 3) or 3
    budget   = state.get("trip_budget", 0) or 0
    style    = state.get("trip_style", "general")
    warnings = state.setdefault("warnings", [])
    trace    = state.setdefault("trace", [])

    if not place:
        state["budget_info"]    = "Budget details not available — destination missing."
        state["cost_breakdown"] = {}
        state["warnings"]       = warnings
        return state

    # ── MCP TOOL 2 — live cost research (3 searches) ──────────────────────────
    hotel_data    = search_serper(f"average hotel cost per night in {place}", 3)
    food_data     = search_serper(f"average daily food cost tourists in {place}", 3)
    activity_data = search_serper(f"tourist activity sightseeing cost in {place}", 3)

    research = "\n".join([
        _titles(hotel_data),
        _titles(food_data),
        _titles(activity_data),
    ]).strip() or "No live cost data."

    budget_str = str(int(budget)) if budget > 0 else "not provided"

    # ── Gemini — structured budget estimate ───────────────────────────────────
    prompt = f"""Travel cost estimator. Estimate in Indian Rupees (INR).

Destination: {place} | Days: {days} | Style: {style} | User budget: INR {budget_str}

Live cost research:
{research}

Return ONLY JSON (no markdown):
{{
  "accommodation":        <int>,
  "food":                 <int>,
  "local_transport":      <int>,
  "sightseeing":          <int>,
  "intercity_transport":  <int>,
  "total":                <int>,
  "per_day":              [<int>, ...],
  "notes":                "<one short sentence>",
  "status":               "ok | tight | over"
}}

Rules:
- per_day must have exactly {days} integers that sum to total.
- Vary per_day (arrival/departure days cost less than full sightseeing days).
- total = sum of the five categories.
- Set status to "over" if user budget < estimate.
"""
    data = extract_json(call_gemini(prompt))
    cats = ["accommodation", "food", "local_transport", "sightseeing", "intercity_transport"]

    cats_labels = [
        ("Accommodation",    "accommodation"),
        ("Food",             "food"),
        ("Local transport",  "local_transport"),
        ("Sightseeing",      "sightseeing"),
        ("Intercity travel", "intercity_transport"),
    ]

    if isinstance(data, dict) and all(k in data for k in cats):
        try:
            data["total"] = sum(int(data.get(c, 0)) for c in cats)
        except Exception:
            pass

        if budget and isinstance(data.get("total"), (int, float)) and data["total"] > budget:
            warnings.append("Estimated cost is higher than your stated budget.")

        lines = [f"Budget estimate for {place} ({days} days):", ""]
        for label, key in cats_labels:
            lines.append(f"- {label}: Rs {int(data.get(key, 0)):,}")
        lines.append(f"- Total: Rs {int(data.get('total', 0)):,}")
        if data.get("per_day"):
            lines.append("- Per day: " + ", ".join(
                f"Day {i+1} Rs {c:,}" for i, c in enumerate(data["per_day"])
            ))
        if data.get("notes"):
            lines.append(f"- Note: {data['notes']}")

        state["budget_info"]    = "\n".join(lines)
        state["cost_breakdown"] = data
    else:
        state["budget_info"]    = "Could not estimate the budget."
        state["cost_breakdown"] = {}
        warnings.append("Budget estimate unavailable — check GEMINI_API_KEY.")

    state["warnings"] = warnings
    trace.append({
        "step":   "Budget",
        "source": "MCP TOOL 2: web_search x3 (Serper) + Gemini",
        "output": state.get("cost_breakdown") or state["budget_info"],
    })
    return state
