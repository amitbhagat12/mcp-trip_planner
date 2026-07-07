# Smart Trip Planner — MCP Final

## Project Structure

```
FINAL_PROJECT/
├── agents/
│   ├── planner.py            ← extracts trip params (Gemini / regex)
│   ├── weather_agent.py      ← calls MCP TOOL 1: get_weather
│   ├── destination_agent.py  ← calls MCP TOOL 4 + TOOL 2: wikipedia + serper
│   ├── transport_agent.py    ← calls MCP TOOL 2: web_search x2
│   ├── budget_agent.py       ← calls MCP TOOL 2: web_search x3
│   └── itinerary_agent.py    ← calls MCP TOOL 3: get_hotels + Gemini
│
├── graph/
│   ├── state.py              ← TripState TypedDict
│   ├── replan.py             ← selective replanning logic
│   └── workflow.py           ← LangGraph pipeline (invoke_smart)
│
├── mcp_client/               ← MCP CLIENT
│   ├── client.py             ← MCPClient: spawns server, sends JSON-RPC calls
│   └── tools.py              ← 4 tool functions agents import from
│
├── mcp_server/               ← MCP SERVER
│   └── server.py             ← 4 MCP tools registered + dispatched
│
├── services/                 ← raw API service functions
│   ├── weather_service.py    ← OpenWeather API
│   ├── serper_service.py     ← Serper (Google Search) API
│   ├── foursquare_service.py ← Foursquare Places API
│   ├── wikipedia_service.py  ← Wikipedia REST API (no key needed)
│   └── llm.py                ← Gemini wrapper
│
├── utils/
│   └── helpers.py            ← regex extraction helpers
│
├── prompts/                  ← (extend with prompt templates)
├── app.py                    ← Streamlit chat UI
├── requirements.txt
├── .env.example
└── mcp_config.json           ← Claude Desktop config
```

---

## How MCP Works Here

```
app.py
  └── graph/workflow.py (invoke_smart)
        └── agents/*.py
              └── mcp_client/tools.py   ← 4 functions
                    └── mcp_client/client.py  ← JSON-RPC over stdio
                          └── mcp_server/server.py  ← 4 MCP tools
                                └── services/*.py  ← actual API calls
```

### The 4 MCP Tools

| Tool | API | Used by |
|---|---|---|
| `get_weather` | OpenWeather | weather_agent |
| `web_search` | Serper | destination_agent, transport_agent, budget_agent |
| `get_wikipedia_summary` | Wikipedia (free) | destination_agent |

### The 4 mcp_client/tools.py functions (match your photo exactly)

```python
def get_weather(city)              → get_client().call_tool("get_weather", ...)
def search_serper(query, n)        → get_client().call_tool("web_search", ...)
def get_hotels(city, limit)        → get_client().call_tool("get_hotels", ...)
def get_wikipedia_summary(place)   → get_client().call_tool("get_wikipedia_summary", ...)
```

---

## Setup & Run

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Create `.env`
```bash
cp .env.example .env
# Fill in your actual keys
```

### 3. Run Streamlit app
```bash
streamlit run app.py
```
The app automatically starts the MCP server as a subprocess — you don't need to start it separately.

### 4. Run MCP server standalone (for Claude Desktop / MCP Inspector)
```bash
python mcp_server/server.py
```

### 5. Test with MCP Inspector
```bash
pip install mcp-inspector
mcp-inspector python mcp_server/server.py
```

---

## Replanning (unchanged from previous version)

| Changed field | Agents that re-run |
|---|---|
| Destination | All 5 |
| Travel dates | weather, destination, itinerary |
| Number of days | destination, budget, itinerary |
| Budget | budget, itinerary ← weather/transport skipped |
| Trip style | destination, itinerary |
