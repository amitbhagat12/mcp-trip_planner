# # """
# # services/wikipedia_service.py
# # Destination overview from Wikipedia REST API — no API key required.
# # Called directly by mcp_server/server.py (TOOL 4: get_wikipedia_summary).
# # """
# # import requests


# # def get_wikipedia_summary(place: str) -> dict:
# #     """
# #     Fetch the intro/summary of a destination's Wikipedia page.
# #     Returns dict with 'title' and 'summary' — or error key.
# #     No API key needed; Wikipedia is free and open.
# #     """
# #     if not place:
# #         return {"error": "No place provided", "summary": ""}
# #     try:
# #         url  = (f"https://en.wikipedia.org/api/rest_v1/page/summary/"
# #                 f"{requests.utils.quote(place)}")
# #         resp = requests.get(
# #             url,
# #             headers={"User-Agent": "TripPlannerBot/1.0 (educational project)"},
# #             timeout=10,
# #         )
# #         # Fallback: try "<place> tourism"
# #         if resp.status_code == 404:
# #             url  = (f"https://en.wikipedia.org/api/rest_v1/page/summary/"
# #                     f"{requests.utils.quote(place + ' tourism')}")
# #             resp = requests.get(
# #                 url,
# #                 headers={"User-Agent": "TripPlannerBot/1.0"},
# #                 timeout=10,
# #             )
# #         if resp.status_code != 200:
# #             return {"error": f"Wikipedia article not found for {place}", "summary": ""}

# #         data    = resp.json()
# #         extract = data.get("extract", "")
# #         title   = data.get("title", place)

# #         # Trim to ~300 words to keep prompts lean
# #         words = extract.split()
# #         if len(words) > 300:
# #             extract = " ".join(words[:300]) + "..."

# #         return {"title": title, "summary": extract}
# #     except Exception as e:
# #         return {"error": str(e), "summary": ""}

# import requests

# HEADERS = {
#     "User-Agent": "TripPlannerBot/1.0 (educational project)"
# }

# def get_wikipedia_summary(place: str) -> dict:
#     """
#     Fetch Wikipedia summary for a place.
#     Returns:
#         {
#             "title": str,
#             "summary": str
#         }
#     """

#     if not place:
#         return {"error": "No place provided", "summary": ""}

#     try:
#         url = (
#             f"https://en.wikipedia.org/api/rest_v1/page/summary/"
#             f"{requests.utils.quote(place)}"
#         )

#         resp = requests.get(
#             url,
#             headers=HEADERS,
#             timeout=10
#         )

#         # Fallback: "<place> tourism"
#         if resp.status_code == 404:
#             fallback_url = (
#                 f"https://en.wikipedia.org/api/rest_v1/page/summary/"
#                 f"{requests.utils.quote(place + ' tourism')}"
#             )

#             resp = requests.get(
#                 fallback_url,
#                 headers=HEADERS,
#                 timeout=10
#             )

#         if resp.status_code != 200:
#             return {
#                 "error": f"Wikipedia article not found for {place}",
#                 "summary": ""
#             }

#         data = resp.json()

#         extract = data.get("extract", "")
#         title = data.get("title", place)

#         # Limit size
#         words = extract.split()
#         if len(words) > 300:
#             extract = " ".join(words[:300]) + "..."

#         return {
#             "title": title,
#             "summary": extract
#         }

#     except requests.exceptions.Timeout:
#         return {
#             "error": "Wikipedia request timed out",
#             "summary": ""
#         }

#     except Exception as e:
#         return {
#             "error": str(e),
#             "summary": ""
#         }

"""
services/wikipedia_service.py

Destination overview from Wikipedia REST API.
No API key required.
"""

import requests

HEADERS = {
    "User-Agent": "TripPlannerBot/1.0 (educational project)"
}


def get_wikipedia_summary(place: str) -> dict:
    """
    Fetch Wikipedia summary for a destination.

    Returns:
    {
        "title": str,
        "summary": str
    }

    or

    {
        "error": str,
        "summary": ""
    }
    """

    if not place:
        return {
            "error": "No place provided",
            "summary": ""
        }

    try:
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            f"{requests.utils.quote(place)}"
        )

        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        # Fallback search: "<place> tourism"
        if resp.status_code == 404:
            fallback_url = (
                "https://en.wikipedia.org/api/rest_v1/page/summary/"
                f"{requests.utils.quote(place + ' tourism')}"
            )

            resp = requests.get(
                fallback_url,
                headers=HEADERS,
                timeout=10
            )

        if resp.status_code != 200:
            return {
                "error": f"Wikipedia article not found for {place}",
                "summary": ""
            }

        data = resp.json()

        title = data.get("title", place)
        summary = data.get("extract", "")

        # Keep prompt size manageable
        words = summary.split()
        if len(words) > 300:
            summary = " ".join(words[:300]) + "..."

        return {
            "title": title,
            "summary": summary
        }

    except requests.exceptions.Timeout:
        return {
            "error": "Wikipedia request timed out",
            "summary": ""
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Wikipedia request failed: {str(e)}",
            "summary": ""
        }

    except Exception as e:
        return {
            "error": str(e),
            "summary": ""
        }
