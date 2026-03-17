import requests

API_KEY = "716409e3a8fcff9ab6e836f337bb0a1e"

# ✅ Valid district → use state for better OpenWeatherMap accuracy
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5).json()

        # ✅ CRITICAL FIX: If city not found, return None (not fake zeros)
        if res.get("cod") != 200:
            return None  # Caller must handle this as invalid city

        rain_mm = 0
        if "rain" in res:
            if isinstance(res["rain"], dict):
                rain_mm = res["rain"].get("1h", res["rain"].get("3h", 0))
            else:
                rain_mm = res.get("rain", 0)

        return {
            "temp": res["main"]["temp"],
            "humidity": res["main"]["humidity"],
            "rain": rain_mm,
            "city_found": True  # ✅ Explicit confirmation city was valid
        }

    except requests.exceptions.Timeout:
        return {"error": "timeout", "temp": "--", "humidity": "--", "rain": 0, "city_found": False}
    except Exception as e:
        print(f"Weather API Error: {e}")
        return {"error": str(e), "temp": "--", "humidity": "--", "rain": 0, "city_found": False}