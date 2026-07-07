"""
graph/replan.py
Selective replanning — only re-run agents whose inputs changed.

Replanning is ONLY triggered after a complete itinerary already exists.
While the user is still providing initial trip details (multi-message),
all agents run every time (is_first_run = True).

Dependency map:
  trip_place  → all agents (everything is place-specific)
  trip_dates  → weather, destination, itinerary
  trip_days   → destination, budget, itinerary
  trip_budget → budget, itinerary         ← weather/transport NOT re-run
  trip_style  → destination, itinerary
"""

from typing import Set

FIELD_AGENT_MAP = {
    "trip_place":  {"weather", "destination", "transport", "budget", "itinerary"},
    "trip_dates":  {"weather", "destination", "itinerary"},
    "trip_days":   {"destination", "budget", "itinerary"},
    "trip_budget": {"budget", "itinerary"},
    "trip_style":  {"destination", "itinerary"},
}

ALL_AGENTS = ["weather", "destination", "transport", "budget", "itinerary"]


def detect_changed_fields(prev_state: dict, new_state: dict) -> Set[str]:
    """Compare previous and new state — return fields that actually changed."""
    changed = set()
    for field in FIELD_AGENT_MAP:
        old_val = prev_state.get(field)
        new_val = new_state.get(field)
        if isinstance(old_val, str):
            old_val = old_val.strip().lower()
        if isinstance(new_val, str):
            new_val = new_val.strip().lower()
        if old_val != new_val and new_val is not None:
            changed.add(field)
    return changed


def agents_to_run(changed_fields: Set[str], is_first_run: bool) -> list:
    """Return the ordered list of agents that need to run this turn."""
    if is_first_run:
        # No complete plan yet — always run everything
        return ALL_AGENTS
    if not changed_fields:
        # Plan exists and nothing changed — skip all
        return []
    needed: Set[str] = set()
    for field in changed_fields:
        needed |= FIELD_AGENT_MAP.get(field, set())
    # Itinerary always re-runs if any other agent runs
    if needed - {"itinerary"}:
        needed.add("itinerary")
    return [a for a in ALL_AGENTS if a in needed]


def describe_replan(changed_fields: Set[str], agents: list, is_first_run: bool = True) -> str:
    """Human-readable explanation of what is happening this turn."""

    # Still collecting info — no complete plan yet
    if is_first_run:
        return f"Generating first plan — running all agents: {', '.join(agents)}."

    # Plan exists, nothing changed
    if not changed_fields:
        return "No changes detected — skipping all agents (using cached plan)."

    # Plan exists, something changed → replan
    field_labels = {
        "trip_place":  "destination",
        "trip_dates":  "travel dates",
        "trip_days":   "trip duration",
        "trip_budget": "budget",
        "trip_style":  "trip style",
    }
    changed_readable = [field_labels.get(f, f) for f in changed_fields]
    skipped          = [a for a in ALL_AGENTS if a not in agents]
    msg  = f"Changed: {', '.join(changed_readable)}. "
    msg += f"Re-running: {', '.join(agents)}."
    if skipped:
        msg += f" Skipping (cached): {', '.join(skipped)}."
    return msg
