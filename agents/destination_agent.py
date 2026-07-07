"""
agents/destination_agent.py
Uses MCP TOOL 3 (get_wikipedia_summary) via mcp_client/tools.py,
then passes the Wikipedia content to Gemini to extract tourist places.
Serper is NOT used here — Wikipedia + Gemini only.
"""

from mcp_client.tools import get_wikipedia_summary
from services.llm import call_gemini


def destination_agent(state: dict) -> dict:
    print("running destination agent  →  MCP TOOL 3: get_wikipedia_summary (Wikipedia) + Gemini")

    place    = state.get("trip_place", "")
    days     = state.get("trip_days", 3) or 3
    style    = state.get("trip_style", "general")
    dates    = state.get("trip_dates", "Not specified")
    warnings = state.setdefault("warnings", [])
    trace    = state.setdefault("trace", [])

    if not place:
        state["place_info"] = "Destination details not available."
        trace.append({"step": "Destination", "source": "skipped", "output": "no place"})
        return state

    # ── MCP TOOL 3 — Wikipedia ────────────────────────────────────────────────
    wiki_result = get_wikipedia_summary(place=place)

    if isinstance(wiki_result, dict) and "error" not in wiki_result:
        wiki_text = (
            f"Wikipedia — {wiki_result.get('title', place)}:\n"
            f"{wiki_result.get('summary', '')}"
        )
    else:
        wiki_text = f"Wikipedia not available for {place}."
        warnings.append(f"Wikipedia: {wiki_result.get('error', '')}")

    # ── Gemini — extract tourist places from Wikipedia content ────────────────
    prompt = f"""You are a travel destination expert.

Trip details: {place} | {days} days | {style} style | traveling in {dates}

--- Wikipedia Content ---
{wiki_text}

Based on the Wikipedia content above, extract 6-8 real tourist places to visit in {place}.

Rules:
- Only real tourist places: landmarks, beaches, forts, museums, markets, temples, viewpoints, nature spots.
- No blog names, website names, or URLs.
- Each entry: place name + one short practical reason to visit.
- If Wikipedia does not have enough places, use your general knowledge about {place} to fill in well-known spots.

Output format (strictly follow this):
Top places to explore in {place}:

1. Place Name
   Reason to visit.

2. Place Name
   Reason to visit.
"""
    place_info = call_gemini(prompt) or f"Could not generate destination list for {place}."
    state["place_info"] = place_info

    trace.append({
        "step":   "Destination",
        "source": "MCP TOOL 3: get_wikipedia_summary (Wikipedia) + Gemini",
        "output": place_info[:300],
    })
    state["warnings"] = warnings
    return state
