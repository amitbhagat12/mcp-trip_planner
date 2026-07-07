"""
agents/planner.py
Extracts trip parameters from user input using Gemini (or regex fallback).
Does NOT call any MCP tool — runs purely on local LLM / regex.
"""

from services.llm import call_gemini, extract_json, llm_enabled
from utils.helpers import (
    extract_place_from_input, extract_days_from_input, extract_budget_from_input,
    extract_month_from_input, extract_style_from_input,
)


def planner_agent(state: dict) -> dict:
    print("running planner agent (extract + validate)")

    user_input   = state.get("user_input", "")
    chat_history = state.get("chat_history", [])
    full_context = "\n".join(chat_history + [user_input]).strip()

    extracted = _extract_with_llm(full_context) if llm_enabled() else None
    if not isinstance(extracted, dict):
        extracted = _extract_with_rules(user_input)

    # Merge: keep existing state values unless the new message provides something
    place = (extracted.get("destination") or "").strip() or state.get("trip_place", "")
    dates = (extracted.get("dates") or "").strip()      or state.get("trip_dates", "")
    style = (extracted.get("style") or "").strip()      or state.get("trip_style", "general")

    try:
        days = int(extracted.get("days") or 0)
    except Exception:
        days = 0
    days = days or state.get("trip_days", 0)

    try:
        budget = float(extracted.get("budget") or 0)
    except Exception:
        budget = 0.0
    budget = budget or state.get("trip_budget", 0.0)

    state["trip_place"]  = place
    state["trip_dates"]  = dates if dates and dates.lower() not in ("not specified", "none", "null") else ""
    state["trip_days"]   = days
    state["trip_style"]  = style or "general"
    state["trip_budget"] = budget

    # ── Validate required fields ──────────────────────────────────────────────
    place  = (state.get("trip_place") or "").strip()
    dates  = (state.get("trip_dates") or "").strip()
    budget = state.get("trip_budget", 0) or 0

    missing = []
    if not place:
        missing.append("destination")
    if not dates or dates.lower() in ("not specified", "none", "null"):
        missing.append("travel month")
    try:
        if float(budget) <= 0:
            missing.append("budget (approx, in INR)")
    except Exception:
        missing.append("budget (approx, in INR)")

    state["need_clarification"] = len(missing) > 0
    state["missing_fields"]     = missing

    state.setdefault("trace", []).append({
        "step":   "Planner",
        "source": "Gemini extract" if llm_enabled() else "regex parse",
        "output": {
            "extracted": {
                "destination": place,
                "dates":  state["trip_dates"],
                "days":   days,
                "budget": budget,
                "style":  state["trip_style"],
            },
            "validation": (
                "Missing: " + ", ".join(missing)
                if missing
                else "All required info present — planning the trip."
            ),
        },
    })
    return state


# ── Private helpers ───────────────────────────────────────────────────────────

def _extract_with_llm(context: str):
    prompt = f"""
You extract travel facts from a conversation. Use the WHOLE conversation; if the
user changes a value, use the latest one. Do not invent values that aren't stated.

Conversation:
{context}

Reply ONLY with JSON (no markdown, no prose):
{{
  "destination": "",
  "days": 0,
  "budget": 0,
  "style": "general",
  "dates": "Not specified"
}}
"""
    data = extract_json(call_gemini(prompt))
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else None


def _extract_with_rules(text: str):
    return {
        "destination": extract_place_from_input(text),
        "days":        extract_days_from_input(text),
        "budget":      extract_budget_from_input(text),
        "style":       extract_style_from_input(text),
        "dates":       extract_month_from_input(text) or "Not specified",
    }
