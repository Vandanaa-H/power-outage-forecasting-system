"""
Test OpenWeather connectivity for Karnataka cities using keys from .env.
This script is non-invasive and safe to run anytime.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Ensure repository root and src are on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
for p in (REPO_ROOT, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Local imports (robust fallback)
try:
    from src.weather.karnataka_weather_api import KarnatakaWeatherAPI
except ModuleNotFoundError:
    from weather.karnataka_weather_api import KarnatakaWeatherAPI


async def main(city: Optional[str] = None):
    load_dotenv()

    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    weatherapi_key = os.getenv("WEATHERAPI_KEY")

    if not openweather_key:
        print("[ERROR] OPENWEATHER_API_KEY not found in .env. Please set it and retry.")
        return 1

    api = KarnatakaWeatherAPI(openweather_api_key=openweather_key, weatherapi_key=weatherapi_key)

    # If city is specified, test single city; otherwise test all
    if city:
        if city.lower() not in api.karnataka_cities:
            print(f"[ERROR] Unknown city '{city}'. Choose from: {', '.join(sorted(api.karnataka_cities.keys()))}")
            return 1
        coords = api.karnataka_cities[city.lower()]
        print(f"[INFO] Testing OpenWeather for {city} ({coords['lat']}, {coords['lon']})...")
        data = await api.get_openweather_current(city.lower(), coords['lat'], coords['lon'])
        if data:
            print("[OK] OpenWeather current weather fetched successfully:")
            print(f"  temp={data.temperature}°C, humidity={data.humidity}%, wind={data.wind_speed} km/h, rain={data.rainfall} mm, desc='{data.weather_description}'")
            return 0
        else:
            print("[ERROR] Failed to fetch OpenWeather data. Check API key, internet, or rate limits.")
            return 2
    else:
        print("[INFO] Testing OpenWeather for all Karnataka cities (this may take ~10-20s)...")
        results = await api.get_current_weather_all_cities()
        if results:
            print(f"[OK] Retrieved weather for {len(results)} cities. Sample:")
            sample = results[0]
            print(f"  {sample.city}: temp={sample.temperature}°C, humidity={sample.humidity}%, wind={sample.wind_speed} km/h, rain={sample.rainfall} mm")
            return 0
        else:
            print("[ERROR] No results. Verify network connectivity and API key.")
            return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenWeather API connectivity for Karnataka.")
    parser.add_argument("--city", type=str, default=None, help="Specific city (e.g., bangalore, mysore). Default: all")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.city)))
