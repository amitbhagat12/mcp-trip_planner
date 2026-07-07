"""
agents/weather_agent.py
Calls MCP TOOL 1 (get_weather) via mcp_client/tools.py,
then uses Gemini to produce a travel weather summary.
"""

from mcp_client.tools import get_weather
from services.llm import call_gemini


def weather_agent(state: dict) -> dict:
    print("running weather agent  →  MCP TOOL 1: get_weather (OpenWeather)")

    place    = state.get("trip_place", "")
    dates    = state.get("trip_dates", "Not specified")
    days     = state.get("trip_days", 3) or 3
    style    = state.get("trip_style", "general")
    warnings = state.setdefault("warnings", [])
    trace    = state.setdefault("trace", [])

    if not place:
        state["weather_info"] = "Weather information not available — destination missing."
        state["best_time"]    = "Best-time information not available."
        warnings.append("Destination missing. Could not fetch weather.")
        trace.append({"step": "Weather", "source": "skipped", "output": "no place"})
        return state

    # ── MCP TOOL 1 ────────────────────────────────────────────────────────────
    live = get_weather(city=place)

    if isinstance(live, dict) and "error" not in live:
        live_text = (
            f"Current live weather in {place}:\n"
            f"- Temperature: {live.get('temp_celsius')}°C\n"
            f"- Condition:   {live.get('description')}\n"
            f"- Humidity:    {live.get('humidity')}%"
        )
    else:
        live_text = f"Live weather unavailable for {place}: {live.get('error','unknown error')}"
        warnings.append(f"OpenWeather: {live.get('error','')}")

    # ── Gemini: create travel summary ─────────────────────────────────────────
    prompt = f"""You are a travel weather assistant. Write a concise Celsius-only report.

Trip: {place} | {dates} | {days} days | {style} style

Live OpenWeather data:
{live_text}

Output format exactly:

Weather summary for {place}:

Current weather:
- Temperature: ...
- Condition:   ...
- Humidity:    ...

Travel outlook for {dates}:
...

Travel advice:
- ...

Best time guidance:
...
"""
    weather_output = call_gemini(prompt) or live_text

    best_time = ""
    if "Best time guidance:" in weather_output:
        best_time = weather_output.split("Best time guidance:", 1)[1].strip()

    state["weather_info"] = weather_output
    state["best_time"]    = best_time or "Best-time information not available."

    trace.append({
        "step":   "Weather",
        "source": "MCP TOOL 1: get_weather (OpenWeather) + Gemini",
        "output": {"weather": weather_output[:300], "best_time": best_time[:150]},
    })
    return state
