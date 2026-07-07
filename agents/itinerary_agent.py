"""
agents/itinerary_agent.py
Uses Gemini only to compose the full day-by-day itinerary.
Foursquare is NOT used here — removed due to API errors.
Stay section uses Gemini's general knowledge for accommodation suggestions.
"""

from services.llm import call_gemini


def itinerary_agent(state: dict) -> dict:
    print("running itinerary agent  →  Gemini only (no Foursquare)")

    place    = state.get("trip_place", "")
    warnings = state.setdefault("warnings", [])
    trace    = state.setdefault("trace", [])
    days     = state.get("trip_days", 3) or 3

    if not place:
        state["final_itinerary"] = "Please provide a destination to generate an itinerary."
        return state

    # ── Per-day spend text ────────────────────────────────────────────────────
    cost_breakdown = state.get("cost_breakdown") or {}
    per_day_txt    = ""
    if cost_breakdown.get("per_day"):
        per_day_txt = "Use these per-day spend figures: " + ", ".join(
            f"Day {i+1} = Rs {c}" for i, c in enumerate(cost_breakdown["per_day"])
        )

    budget       = state.get("trip_budget", 0) or 0
    budget_label = f"INR {int(budget)}" if budget > 0 else "not provided"

    # ── Gemini — full day-by-day itinerary ────────────────────────────────────
    prompt = f"""You are a friendly, practical travel planner.
Write a guided day-by-day itinerary in Markdown for a {days}-day {state.get('trip_style','general')} trip to {place} ({state.get('trip_dates','')}).

Use the real information provided below, and your knowledge of {place} for any gaps:

BEST TIME TO VISIT:
{state.get('best_time') or 'Not available'}

WEATHER:
{state.get('weather_info') or 'Not available'}

TOP PLACES TO VISIT:
{state.get('place_info') or 'Not available'}

TRANSPORT:
{state.get('transport_info') or 'Not available'}

BUDGET BREAKDOWN:
{state.get('budget_info') or 'Not available'}

User's budget: {budget_label}
{per_day_txt}

FORMAT (strict — follow exactly):
For each day, use a header exactly like '### Day 1 - <short theme>' then:
- **Morning:** what to do (1-2 sentences)
- **Afternoon:** ...
- **Evening:** ...
- **Stay:** Recommend a well-known hotel area or budget/mid-range hotel type for {place} (use your knowledge)
- **Approx cost:** Rs <per-day figure>

Day 1 morning = arrival and check-in.
Last day = checkout and departure.

After the days add:

## 💰 Expense Summary
Markdown table: Accommodation | Food | Local transport | Sightseeing | Intercity travel | Total
One line: whether this fits the user's budget.

## Why these choices?
2-3 lines of key reasoning about why these places and this schedule work well.
"""
    itinerary = call_gemini(prompt) or "Could not generate itinerary (LLM unavailable)."

    state["final_itinerary"] = itinerary
    state["warnings"]        = warnings

    trace.append({
        "step":   "Itinerary",
        "source": "Gemini (no external API)",
        "output": f"{days}-day itinerary composed for {place}",
    })
    return state
