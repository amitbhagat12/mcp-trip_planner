"""
app.py — Streamlit UI for Smart Trip Planner (MCP Edition)

MCP Tools used:
  TOOL 1: get_weather           → weather_agent    (OpenWeather)
  TOOL 2: web_search            → transport_agent, budget_agent  (Serper)
  TOOL 3: get_wikipedia_summary → destination_agent (Wikipedia)
  

Destination agent: Wikipedia + Gemini only (no Serper)
Itinerary agent:   Gemini only (no Foursquare)
"""

import streamlit as st
from graph.workflow import invoke_smart

st.set_page_config(page_title="Smart Trip Planner", page_icon="✈️", layout="wide")
st.title("✈️ Smart Trip Planning Assistant")

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "trip_state" not in st.session_state:
    st.session_state.trip_state = {}


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Agent Outputs")
    state = st.session_state.trip_state

    choice = st.selectbox(
        "Select agent output:",
        [
            "Weather & best time",
            "Destination (Wikipedia + Gemini)",
            "Transport (Serper)",
            "Budget (Serper + Gemini)",
            "Final Itinerary",
        ],
    )

    if choice == "Weather & best time":
        st.write(state.get("weather_info") or "Not available yet.")
        st.markdown(f"**Best time:** {state.get('best_time') or 'Not available yet.'}")

    elif choice == "Destination (Wikipedia + Gemini)":
        st.write(state.get("place_info") or "Not available yet.")

    elif choice == "Transport (Serper)":
        st.write(state.get("transport_info") or "Not available yet.")

    elif choice == "Budget (Serper + Gemini)":
        st.write(state.get("budget_info") or "Not available yet.")

    elif choice == "Final Itinerary":
        st.write(state.get("final_itinerary") or "Not available yet.")

    # Warnings
    if state.get("warnings"):
        st.divider()
        st.subheader("⚠️ Warnings")
        for w in state["warnings"]:
            st.warning(w)

    # Replan info
    replan_msg = state.get("_replan_message", "")
    if replan_msg:
        st.divider()
        st.subheader("♻️ Replan Info")
        st.info(replan_msg)
        changed = state.get("_changed_fields", [])
        if changed:
            st.markdown(f"**Changed:** `{'`, `'.join(changed)}`")
        ran     = state.get("_replan_agents", [])
        skipped = [a for a in ["weather","destination","transport","budget","itinerary"]
                   if a not in ran]
        if ran:
            st.markdown(f"**Ran:** `{'`, `'.join(ran)}`")
        if skipped:
            st.markdown(f"**Skipped (cached):** `{'`, `'.join(skipped)}`")

    # MCP tool map
    st.divider()
    st.subheader("🔌 MCP Tools (3)")
    st.markdown("""
| # | Tool | API | Used by |
|---|---|---|---|
| 1 | `get_weather` | OpenWeather | weather_agent |
| 2 | `web_search` | Serper | transport, budget |
| 3 | `get_wikipedia_summary` | Wikipedia | destination_agent |
""")


# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Describe your trip… e.g. '3-day trip to Goa in December, budget 30000'"
)

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Planning your trip via MCP tools…"):

            prev_state = st.session_state.trip_state.copy()

            current = prev_state.copy()
            current["user_input"]   = user_input
            current["chat_history"] = [
                m["content"] for m in st.session_state.chat_history if m["role"] == "user"
            ]
            current["trace"]    = []
            current["warnings"] = []

            result, replan_msg = invoke_smart(current, prev_state)
            st.session_state.trip_state = result

            # ── Response ───────────────────────────────────────────────────────
            if result.get("need_clarification"):
                response = (
                    "I need a bit more info. Could you please tell me your **"
                    + "**, **".join(result.get("missing_fields", []))
                    + "**?"
                )
                st.warning(response)

            elif result.get("final_itinerary"):
                changed      = result.get("_changed_fields", [])
                ran_agents   = result.get("_replan_agents", [])
                # prev_state had a complete plan → this is a replan
                was_replanned = bool(prev_state.get("final_itinerary", "").strip()) and bool(changed)

                if was_replanned:
                    label_map = {
                        "trip_place":  "destination",
                        "trip_dates":  "travel dates",
                        "trip_days":   "trip duration",
                        "trip_budget": "budget",
                        "trip_style":  "trip style",
                    }
                    readable = [label_map.get(f, f) for f in changed]
                    response = (
                        f"♻️ **Replanned!** Updated: `{'`, `'.join(readable)}`\n\n"
                        f"Agents re-ran: `{'`, `'.join(ran_agents)}`\n\n"
                        f"✅ Trip plan updated!"
                    )
                else:
                    response = (
                        "✅ Trip plan generated!\n\n"
                        "📍 Destinations via **Wikipedia + Gemini** · "
                        "🌤 Weather from **OpenWeather** · "
                        "💰 Costs via **Serper**"
                    )
                st.success(response)

            else:
                response = "⚠️ Couldn't generate the plan yet. Please add more details."
                st.warning(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})


# ── Final itinerary ────────────────────────────────────────────────────────────
st.divider()
st.subheader("🗺 Final Trip Plan")

if st.session_state.trip_state.get("final_itinerary"):
    st.markdown(st.session_state.trip_state["final_itinerary"])
else:
    st.info("Your full itinerary will appear here after planning.")


# ── Behind the scenes trace ────────────────────────────────────────────────────
trace = st.session_state.trip_state.get("trace", [])
if trace:
    with st.expander(f"🔧 Behind the scenes — {len(trace)} MCP tool/API calls"):
        for step in trace:
            st.markdown(f"**{step.get('step')}** · _{step.get('source')}_")
            st.code(str(step.get("output", ""))[:800])
