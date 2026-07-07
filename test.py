# import requests

# headers = {
#     "User-Agent": "MCPTripPlanner/1.0 (amit@example.com)"
# }

# url = "https://en.wikipedia.org/api/rest_v1/page/summary/Chennai"

# r = requests.get(url, headers=headers)

# print(r.status_code)
# print(r.json())

from services.wikipedia_service import get_wikipedia_summary

print(get_wikipedia_summary("Chennai"))
