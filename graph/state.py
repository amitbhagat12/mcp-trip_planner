from typing import TypedDict, List


class TripState(TypedDict, total=False):
    # ── User input ────────────────────────────────────────────────────────────
    user_input:   str
    chat_history: List[str]

    # ── Extracted trip details ────────────────────────────────────────────────
    trip_place:        str
    trip_dates:        str
    trip_days:         int
    trip_style:        str
    trip_budget:       float
    budget_preference: str

    # ── Agent outputs ─────────────────────────────────────────────────────────
    weather_info:    str    # MCP TOOL 1 (OpenWeather) + Gemini
    best_time:       str    # extracted from weather summary
    place_info:      str    # MCP TOOL 3 (Wikipedia) + Gemini
    transport_info:  str    # MCP TOOL 2 (Serper) x2
    budget_info:     str    # formatted budget string
    cost_breakdown:  dict   # MCP TOOL 2 (Serper) x3 + Gemini JSON
    final_itinerary: str    # Gemini only

    # ── Clarification ─────────────────────────────────────────────────────────
    need_clarification: bool
    missing_fields:     List[str]

    # ── Trace & warnings ──────────────────────────────────────────────────────
    trace:    List[dict]
    warnings: List[str]

    # ── Replanning metadata ───────────────────────────────────────────────────
    _replan_agents:  List[str]
    _replan_message: str
    _changed_fields: List[str]
