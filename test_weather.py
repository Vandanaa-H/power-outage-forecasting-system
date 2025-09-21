import asyncio
import sys
sys.path.append('.')
from src.api.routes.weather import get_current_weather, get_weather_forecast

async def test_weather():
    try:
        print('🔧 Testing weather endpoints...')
        
        # Test current weather
        current = await get_current_weather(city='bangalore')
        print('✅ Current Weather: OK')
        print(f'  Temperature: {current.get("temperature", "N/A")}°C')
        print(f'  Status: {current.get("status", "unknown")}')
        
        # Test forecast
        forecast = await get_weather_forecast(city='bangalore', hours=24)
        print('✅ Forecast: OK')
        print(f'  Items count: {len(forecast.get("items", []))}')
        if forecast.get('items'):
            first_item = forecast['items'][0]
            print(f'  First forecast: {first_item.get("temperature", "N/A")}°C')
        
        print('\n🎉 Backend weather endpoints working properly!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_weather())
    sys.exit(0 if success else 1)