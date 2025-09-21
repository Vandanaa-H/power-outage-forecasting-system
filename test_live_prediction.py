#!/usr/bin/env python3
"""
Test the live prediction functionality directly.
"""

import sys
import os
import asyncio
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_live_prediction():
    try:
        print("Testing live prediction functionality...")
        
        # Import required modules
        from src.api.routes.predictions import get_model_instance
        
        # Get the model
        model = get_model_instance()
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Test prediction with sample data
        sample_data = {
            'weather': {
                'temperature': 28.5,
                'humidity': 75,
                'wind_speed': 12,
                'rainfall': 15,
                'lightning_strikes': 3,
                'storm_alert': True
            },
            'grid': {
                'load_factor': 0.85,
                'voltage_stability': 0.75,
                'historical_outages': 5,
                'transformer_load': 0.8,
                'feeder_health': 0.7
            },
            'prediction_horizon': 24
        }
        
        result = await model.predict(sample_data)
        print("✓ Prediction successful:")
        print(f"  Risk Score: {result['risk_score']:.1f}%")
        print(f"  Confidence: {result['confidence_interval']}")
        print(f"  Factors: {result['contributing_factors']}")
        
        # Test live weather integration
        try:
            import aiohttp
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            api_key = os.getenv('OPENWEATHER_API_KEY')
            
            if api_key:
                async with aiohttp.ClientSession() as session:
                    url = f"http://api.openweathermap.org/data/2.5/weather"
                    params = {
                        'q': 'Bengaluru,IN',
                        'appid': api_key,
                        'units': 'metric'
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            weather_data = await response.json()
                            print("✓ Live weather data retrieved:")
                            print(f"  Temperature: {weather_data['main']['temp']}°C")
                            print(f"  Humidity: {weather_data['main']['humidity']}%")
                            print(f"  Weather: {weather_data['weather'][0]['description']}")
                        else:
                            print(f"✗ Weather API error: {response.status}")
            else:
                print("⚠ No API key found for live weather test")
                
        except Exception as e:
            print(f"⚠ Live weather test skipped: {e}")
        
        print("\n✓ Live prediction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Live prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_live_prediction())
    sys.exit(0 if success else 1)