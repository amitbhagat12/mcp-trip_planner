"""
services/weather_service.py
Fetches live weather from OpenWeather API.
Called directly by mcp_server/server.py (TOOL 1: get_weather).
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def get_weather(city: str) -> dict:
    """
    Fetch current weather for a city from OpenWeather.
    Returns dict with temp_celsius, description, humidity — or error key.
    """
    if not OPENWEATHER_KEY:
        return {"error": "OPENWEATHER_API_KEY missing"}
    try:
        url  = (f"http://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={OPENWEATHER_KEY}&units=metric")
        data = requests.get(url, timeout=10).json()
        if data.get("cod") != 200:
            return {"error": data.get("message", "Weather API error")}
        return {
            "city":         city,
            "temp_celsius": data["main"]["temp"],
            "description":  data["weather"][0]["description"],
            "humidity":     data["main"]["humidity"],
        }
    except Exception as e:
        return {"error": str(e)}
