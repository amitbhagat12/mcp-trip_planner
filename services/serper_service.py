"""
services/serper_service.py
Google search via Serper API.
Called directly by mcp_server/server.py (TOOL 2: web_search).
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")


def search_serper(query: str, num_results: int = 5) -> dict:
    """
    Run a Google search via Serper and return organic results.
    Returns dict with 'organic' list — or error key.
    """
    if not SERPER_API_KEY:
        return {"error": "SERPER_API_KEY not found"}
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY":    SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": num_results},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
