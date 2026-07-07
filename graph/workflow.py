"""
graph/workflow.py
Builds and runs a selective LangGraph pipeline.
Agents call MCP tools via mcp_client/tools.py.

Bug fix:
  is_first_run is now True whenever no complete itinerary exists yet.
  This means even if the user sends multiple messages to complete their
  trip details (e.g. first message = destination, second = dates + budget),
  ALL agents run — not just the ones whose fields "changed".
  Replanning only kicks in AFTER a full itinerary has been generated.
"""

from langgraph.graph import StateGraph, END

from graph.state  import TripState
from graph.replan import agents_to_run, detect_changed_fields, describe_replan

from agents.planner           import planner_agent
from agents.weather_agent     import weather_agent
from agents.destination_agent import destination_agent
from agents.transport_agent   import transport_agent
from agents.budget_agent      import budget_agent
from agents.itinerary_agent   import itinerary_agent

AGENT_FN = {
    "weather":     weather_agent,
    "destination": destination_agent,
    "transport":   transport_agent,
    "budget":      budget_agent,
    "itinerary":   itinerary_agent,
}


def route_after_planner(state: dict) -> str:
    return "ask_user" if state.get("need_clarification") else "proceed"


def build_graph(agents: list = None):
    if agents is None:
        agents = list(AGENT_FN.keys())

    graph = StateGraph(TripState)
    graph.add_node("planner", planner_agent)

    for name in agents:
        graph.add_node(name, AGENT_FN[name])

    graph.set_entry_point("planner")

    if agents:
        graph.add_conditional_edges(
            "planner",
            route_after_planner,
            {"ask_user": END, "proceed": agents[0]},
        )
        for i in range(len(agents) - 1):
            graph.add_edge(agents[i], agents[i + 1])
        graph.add_edge(agents[-1], END)
    else:
        graph.add_conditional_edges(
            "planner",
            route_after_planner,
            {"ask_user": END, "proceed": END},
        )

    return graph.compile()


def invoke_smart(current_state: dict, prev_state: dict):
    """
    Called by app.py each turn.

    KEY FIX:
      is_first_run = True  when NO complete itinerary exists yet.
      This covers the case where the user sends multiple messages to
      provide trip details (e.g. destination first, then dates + budget).
      All agents run until a full itinerary is successfully generated.

      is_first_run = False (replanning mode) ONLY when a complete itinerary
      already exists in prev_state. Only then do we selectively re-run agents.
    """
    planner_output = planner_agent(current_state.copy())

    # ── Bug fix: check if a full plan already exists ──────────────────────────
    # Replanning only makes sense AFTER the first complete plan is generated.
    # If no itinerary exists yet, always run ALL agents regardless of what
    # fields appear to have "changed" between messages.
    plan_already_exists = bool(prev_state.get("final_itinerary", "").strip())

    if not plan_already_exists:
        # First time getting a complete plan — run everything
        is_first_run = True
        changed      = set()
    else:
        # A full plan exists — now detect what the user changed
        is_first_run = False
        changed      = detect_changed_fields(prev_state, planner_output)

    agents     = agents_to_run(changed, is_first_run)
    replan_msg = describe_replan(changed, agents, is_first_run)

    print(f"\n[Replan] {replan_msg}")
    print(f"[Replan] Agents running this turn: {agents}\n")

    merged_state = {**prev_state, **planner_output}

    graph  = build_graph(agents)
    result = graph.invoke(merged_state)

    # Restore cached outputs for skipped agents
    for agent in AGENT_FN:
        if agent not in agents and agent in prev_state:
            result[agent] = prev_state[agent]

    result["_replan_agents"]  = agents
    result["_replan_message"] = replan_msg
    result["_changed_fields"] = list(changed)

    return result, replan_msg


if __name__ == "__main__":
    try:
        build_graph().get_graph().draw_mermaid_png(output_file_path="graph_diagram.png")
        print("Graph saved as graph_diagram.png")
    except Exception as e:
        print("Could not render diagram:", e)
