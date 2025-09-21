import asyncio
from src.api.routes.weather import get_weather_forecast

async def test_forecast():
    forecast = await get_weather_forecast(city='bangalore', hours=8)
    print('🌦️ Real-time Forecast Data:')
    print(f'Source: {forecast.get("source", "unknown")}')
    for i, item in enumerate(forecast.get('items', [])[:3]):
        temp = item.get('temperature', 'N/A')
        rain = item.get('rainfall', 0)
        print(f'  Hour {i+1}: {temp}°C, {rain}mm rain')

if __name__ == "__main__":
    asyncio.run(test_forecast())