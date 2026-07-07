# """
# mcp_client/tools.py
# ===================
# 3 tool wrapper functions — agents import from here.

# Each function calls the matching MCP tool via get_client().call_tool()
# instead of importing the service directly.

#   get_weather(city)            → MCP TOOL 1: get_weather           (OpenWeather)
#   search_serper(query, n)      → MCP TOOL 2: web_search            (Serper)
#   get_wikipedia_summary(place) → MCP TOOL 3: get_wikipedia_summary (Wikipedia)
# """

# from mcp_client.client import get_client


# def get_weather(city: str) -> dict:
#     """
#     Same shape as services.weather_service.get_weather, but called
#     over MCP instead of imported directly.
#     """
#     return get_client().call_tool("get_weather", {"city": city})


# def search_serper(query: str, num_results: int = 5) -> dict:
#     """
#     Same shape as services.serper_service.search_serper, but called
#     over MCP instead of imported directly.
#     """
#     return get_client().call_tool("web_search", {"query": query, "num_results": num_results})


# def get_wikipedia_summary(place: str) -> dict:
#     """
#     Same shape as services.wikipedia_service.get_wikipedia_summary, but
#     called over MCP instead of imported directly.
#     """
#     return get_client().call_tool("get_wikipedia_summary", {"place": place})

from mcp_client.client import get_client


def get_weather(city: str) -> dict:
    return get_client().call_tool(
        "get_weather",
        {"city": city}
    )


def search_serper(query: str, num_results: int = 5) -> dict:
    return get_client().call_tool(
        "web_search",
        {
            "query": query,
            "num_results": num_results
        }
    )


def get_wikipedia_summary(place: str) -> dict:
    return get_client().call_tool(
        "get_wikipedia_summary",
        {"place": place}
    )