# """
# mcp_server/server.py
# ====================
# MCP Server using FastMCP with @mcp.tool() decorators.

# 3 tools only:
#   TOOL 1 : get_weather           — OpenWeather API
#   TOOL 2 : web_search            — Serper (Google Search API)
#   TOOL 3 : get_wikipedia_summary — Wikipedia REST API (no key needed)

# Run:
#     python mcp_server/server.py
# """

# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# from mcp.server.fastmcp import FastMCP

# from services.weather_service   import get_weather   as _get_weather
# from services.serper_service    import search_serper as _search_serper
# from services.wikipedia_service import get_wikipedia_summary as _get_wiki

# mcp = FastMCP("trip-planner")


# # ── TOOL 1 ────────────────────────────────────────────────────────────────────
# @mcp.tool()
# def get_weather(city: str) -> dict:
#     """
#     Fetch live current weather for a travel destination using OpenWeather API.
#     Returns temperature in Celsius, weather condition, and humidity.
#     Used by the weather agent to build a travel weather summary.

#     Args:
#         city: City or destination name (e.g. 'Goa', 'Manali', 'Shimla')
#     """
#     return _get_weather(city=city)


# # ── TOOL 2 ────────────────────────────────────────────────────────────────────
# @mcp.tool()
# def web_search(query: str, num_results: int = 5) -> dict:
#     """
#     Search Google using the Serper API and return organic search results.
#     Used by transport agent (how to reach) and budget agent (live cost research).
#     Returns a list of results with title and snippet.

#     Args:
#         query:       Search query string
#         num_results: Number of results to return (default 5)
#     """
#     return _search_serper(query=query, num_results=num_results)


# # ── TOOL 3 ────────────────────────────────────────────────────────────────────
# @mcp.tool()
# def get_wikipedia_summary(place: str) -> dict:
#     """
#     Fetch a factual overview of a travel destination from the Wikipedia REST API.
#     Returns the introduction/summary paragraph of the Wikipedia page.
#     No API key required — Wikipedia is free and open.
#     Used by the destination agent to research tourist places with Gemini.

#     Args:
#         place: Destination name (e.g. 'Goa', 'Rajasthan', 'Manali')
#     """
#     return _get_wiki(place=place)


# # ── Entry point ───────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     mcp.run()

"""
mcp_server/server.py
====================
MCP Server using FastMCP with @mcp.tool() decorators.

3 tools only:
  TOOL 1 : get_weather           — OpenWeather API
  TOOL 2 : web_search            — Serper (Google Search API)
  TOOL 3 : get_wikipedia_summary — Wikipedia REST API (no key needed)

Run:
    python mcp_server/server.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP

from services.weather_service import get_weather as _get_weather
from services.serper_service import search_serper as _search_serper
from services.wikipedia_service import get_wikipedia_summary as _get_wiki

mcp = FastMCP("trip-planner")


# TOOL 1
@mcp.tool()
def get_weather(city: str) -> dict:
    """
    Fetch live current weather for a travel destination.
    """
    return _get_weather(city=city)


# TOOL 2
@mcp.tool()
def web_search(query: str, num_results: int = 5) -> dict:
    """
    Search Google using Serper API.
    """
    return _search_serper(
        query=query,
        num_results=num_results
    )


# TOOL 3
@mcp.tool()
def get_wikipedia_summary(place: str) -> dict:
    """
    Fetch destination summary from Wikipedia.
    """
    return _get_wiki(place=place)


if __name__ == "__main__":
    mcp.run()