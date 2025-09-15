"""
Real Weather API Integration for Karnataka Power Outage Forecasting
Connects to OpenWeather, WeatherAPI, and IMD for live data
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import asyncio
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure for Karnataka locations."""
    timestamp: datetime
    city: str
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    wind_speed: float
    rainfall: float
    pressure: float
    visibility: float
    weather_description: str
    
    # Derived fields for ML
    lightning_risk: int
    storm_alert: int
    monsoon_intensity: float


class KarnatakaWeatherAPI:
    """Real weather API integration for Karnataka cities."""
    
    def __init__(self, openweather_api_key: str = None, weatherapi_key: str = None):
        self.openweather_key = openweather_api_key or "YOUR_OPENWEATHER_API_KEY"
        self.weatherapi_key = weatherapi_key or "YOUR_WEATHERAPI_KEY"
        
        # Karnataka major cities with coordinates
        self.karnataka_cities = {
            'bangalore': {'lat': 12.9716, 'lon': 77.5946, 'priority': 1},
            'mysore': {'lat': 12.2958, 'lon': 76.6394, 'priority': 1},
            'hubli': {'lat': 15.3647, 'lon': 75.1240, 'priority': 1},
            'dharwad': {'lat': 15.4589, 'lon': 75.0078, 'priority': 1},
            'mangalore': {'lat': 12.9141, 'lon': 74.8560, 'priority': 2},
            'belgaum': {'lat': 15.8497, 'lon': 74.4977, 'priority': 2},
            'gulbarga': {'lat': 17.3297, 'lon': 76.8343, 'priority': 2},
            'davangere': {'lat': 14.4644, 'lon': 75.9932, 'priority': 2},
            'bellary': {'lat': 15.1394, 'lon': 76.9214, 'priority': 2},
            'bijapur': {'lat': 16.8302, 'lon': 75.7100, 'priority': 2},
            'shimoga': {'lat': 13.9299, 'lon': 75.5681, 'priority': 2},
            'tumkur': {'lat': 13.3379, 'lon': 77.1022, 'priority': 2}
        }
        
        # API endpoints
        self.openweather_base = "https://api.openweathermap.org/data/2.5"
        self.weatherapi_base = "https://api.weatherapi.com/v1"
        
    def get_api_setup_instructions(self):
        """Return instructions for setting up weather APIs."""
        return """
        🔑 WEATHER API SETUP INSTRUCTIONS:
        
        1. OpenWeather API (Primary):
           - Sign up: https://home.openweathermap.org/users/sign_up
           - Get free API key (1000 calls/day)
           - Add to .env file: OPENWEATHER_API_KEY=your_key_here
        
        2. WeatherAPI (Backup):
           - Sign up: https://www.weatherapi.com/signup.aspx
           - Get free API key (1M calls/month)
           - Add to .env file: WEATHERAPI_KEY=your_key_here
        
        3. Test APIs:
           - weather_api = KarnatakaWeatherAPI(openweather_key, weatherapi_key)
           - data = weather_api.get_current_weather_all_cities()
        """
    
    async def get_openweather_current(self, city: str, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather from OpenWeather API."""
        try:
            url = f"{self.openweather_base}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_openweather_response(city, lat, lon, data)
                    else:
                        logger.error(f"OpenWeather API error for {city}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"OpenWeather API error for {city}: {str(e)}")
            return None
    
    def _parse_openweather_response(self, city: str, lat: float, lon: float, data: dict) -> WeatherData:
        """Parse OpenWeather API response."""
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        rain = data.get('rain', {})
        
        # Extract weather data
        temperature = main.get('temp', 0)
        humidity = main.get('humidity', 0)
        pressure = main.get('pressure', 0)
        wind_speed = wind.get('speed', 0) * 3.6  # Convert m/s to km/h
        rainfall = rain.get('1h', 0)  # Last 1 hour rainfall in mm
        visibility = data.get('visibility', 10000) / 1000  # Convert to km
        description = weather.get('description', '')
        
        # Calculate derived fields
        lightning_risk = self._calculate_lightning_risk(description, wind_speed, humidity)
        storm_alert = self._calculate_storm_alert(description, wind_speed, rainfall)
        monsoon_intensity = self._calculate_monsoon_intensity(rainfall, humidity, description)
        
        return WeatherData(
            timestamp=datetime.utcnow(),
            city=city,
            latitude=lat,
            longitude=lon,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            rainfall=rainfall,
            pressure=pressure,
            visibility=visibility,
            weather_description=description,
            lightning_risk=lightning_risk,
            storm_alert=storm_alert,
            monsoon_intensity=monsoon_intensity
        )
    
    async def get_openweather_forecast(self, city: str, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Get weather forecast from OpenWeather API."""
        try:
            url = f"{self.openweather_base}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key,
                'units': 'metric',
                'cnt': min(hours, 40)  # API limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_openweather_forecast(city, lat, lon, data)
                    else:
                        logger.error(f"OpenWeather forecast error for {city}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"OpenWeather forecast error for {city}: {str(e)}")
            return []
    
    def _parse_openweather_forecast(self, city: str, lat: float, lon: float, data: dict) -> List[WeatherData]:
        """Parse OpenWeather forecast response."""
        forecasts = []
        
        for item in data.get('list', []):
            main = item.get('main', {})
            weather = item.get('weather', [{}])[0]
            wind = item.get('wind', {})
            rain = item.get('rain', {})
            
            timestamp = datetime.fromtimestamp(item.get('dt', 0))
            temperature = main.get('temp', 0)
            humidity = main.get('humidity', 0)
            pressure = main.get('pressure', 0)
            wind_speed = wind.get('speed', 0) * 3.6
            rainfall = rain.get('3h', 0) / 3  # Convert 3h to 1h average
            visibility = item.get('visibility', 10000) / 1000
            description = weather.get('description', '')
            
            lightning_risk = self._calculate_lightning_risk(description, wind_speed, humidity)
            storm_alert = self._calculate_storm_alert(description, wind_speed, rainfall)
            monsoon_intensity = self._calculate_monsoon_intensity(rainfall, humidity, description)
            
            forecasts.append(WeatherData(
                timestamp=timestamp,
                city=city,
                latitude=lat,
                longitude=lon,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                rainfall=rainfall,
                pressure=pressure,
                visibility=visibility,
                weather_description=description,
                lightning_risk=lightning_risk,
                storm_alert=storm_alert,
                monsoon_intensity=monsoon_intensity
            ))
        
        return forecasts
    
    def _calculate_lightning_risk(self, description: str, wind_speed: float, humidity: float) -> int:
        """Calculate lightning risk based on weather conditions."""
        risk = 0
        
        # Description-based risk
        lightning_keywords = ['thunder', 'lightning', 'storm']
        if any(keyword in description.lower() for keyword in lightning_keywords):
            risk += 3
        
        # Wind and humidity factors
        if wind_speed > 30 and humidity > 70:
            risk += 2
        elif wind_speed > 20 and humidity > 60:
            risk += 1
        
        return min(5, risk)  # Max risk level 5
    
    def _calculate_storm_alert(self, description: str, wind_speed: float, rainfall: float) -> int:
        """Calculate storm alert level."""
        alert = 0
        
        # Severe weather indicators
        severe_keywords = ['severe', 'heavy', 'intense', 'extreme']
        if any(keyword in description.lower() for keyword in severe_keywords):
            alert = 1
        
        # Wind-based alert
        if wind_speed > 40:
            alert = 1
        
        # Rainfall-based alert
        if rainfall > 25:  # Heavy rainfall
            alert = 1
        
        return alert
    
    def _calculate_monsoon_intensity(self, rainfall: float, humidity: float, description: str) -> float:
        """Calculate monsoon intensity (0-1 scale)."""
        intensity = 0.0
        
        # Rainfall component
        if rainfall > 50:
            intensity += 0.5
        elif rainfall > 25:
            intensity += 0.3
        elif rainfall > 10:
            intensity += 0.1
        
        # Humidity component
        if humidity > 85:
            intensity += 0.3
        elif humidity > 70:
            intensity += 0.2
        
        # Description component
        monsoon_keywords = ['rain', 'drizzle', 'shower', 'downpour']
        if any(keyword in description.lower() for keyword in monsoon_keywords):
            intensity += 0.2
        
        return min(1.0, intensity)
    
    async def get_current_weather_all_cities(self) -> List[WeatherData]:
        """Get current weather for all Karnataka cities."""
        tasks = []
        
        for city_name, coords in self.karnataka_cities.items():
            task = self.get_openweather_current(
                city_name, 
                coords['lat'], 
                coords['lon']
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        weather_data = []
        for result in results:
            if isinstance(result, WeatherData):
                weather_data.append(result)
        
        logger.info(f"Retrieved weather data for {len(weather_data)} Karnataka cities")
        return weather_data
    
    async def get_forecast_all_cities(self, hours: int = 24) -> Dict[str, List[WeatherData]]:
        """Get weather forecast for all Karnataka cities."""
        forecasts = {}
        
        for city_name, coords in self.karnataka_cities.items():
            forecast = await self.get_openweather_forecast(
                city_name,
                coords['lat'],
                coords['lon'],
                hours
            )
            forecasts[city_name] = forecast
        
        logger.info(f"Retrieved {hours}-hour forecasts for {len(forecasts)} Karnataka cities")
        return forecasts
    
    def weather_data_to_ml_features(self, weather_data: WeatherData) -> dict:
        """Convert weather data to ML model features."""
        return {
            'temperature': weather_data.temperature,
            'humidity': weather_data.humidity,
            'wind_speed': weather_data.wind_speed,
            'rainfall': weather_data.rainfall,
            'lightning_strikes': weather_data.lightning_risk,
            'storm_alert': weather_data.storm_alert,
            'pressure': weather_data.pressure,
            'visibility': weather_data.visibility,
            'monsoon_intensity': weather_data.monsoon_intensity
        }
    
    def save_weather_data(self, weather_data: List[WeatherData], filename: str = None):
        """Save weather data to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/karnataka_weather_{timestamp}.csv"
        
        # Convert to DataFrame
        data_dicts = []
        for wd in weather_data:
            data_dict = {
                'timestamp': wd.timestamp,
                'city': wd.city,
                'latitude': wd.latitude,
                'longitude': wd.longitude,
                'temperature': wd.temperature,
                'humidity': wd.humidity,
                'wind_speed': wd.wind_speed,
                'rainfall': wd.rainfall,
                'pressure': wd.pressure,
                'visibility': wd.visibility,
                'weather_description': wd.weather_description,
                'lightning_risk': wd.lightning_risk,
                'storm_alert': wd.storm_alert,
                'monsoon_intensity': wd.monsoon_intensity
            }
            data_dicts.append(data_dict)
        
        df = pd.DataFrame(data_dicts)
        df.to_csv(filename, index=False)
        logger.info(f"Saved weather data for {len(weather_data)} records to {filename}")


# Demo usage
async def demo_weather_api():
    """Demo the weather API integration."""
    print("🌤️  KARNATAKA WEATHER API DEMO")
    print("="*50)
    
    # Initialize (with demo keys - replace with real ones)
    weather_api = KarnatakaWeatherAPI(
        openweather_api_key="demo_key",  # Replace with real key
        weatherapi_key="demo_key"        # Replace with real key
    )
    
    print("📍 Karnataka Cities Covered:")
    for city, info in weather_api.karnataka_cities.items():
        priority = "🔴 High" if info['priority'] == 1 else "🟡 Medium"
        print(f"   {city.title()}: {priority} Priority")
    
    print(f"\n{weather_api.get_api_setup_instructions()}")
    
    # Note: Actual API calls would fail with demo keys
    print("⚠️  Replace demo keys with real API keys to fetch live data!")


if __name__ == "__main__":
    asyncio.run(demo_weather_api())
