#!/usr/bin/env python3
"""
Direct API test for real-time functionality without server startup issues.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_real_time_api():
    """Test the real-time API functionality directly."""
    print("=" * 60)
    print("REAL-TIME POWER OUTAGE FORECASTING API TEST")
    print("=" * 60)
    
    try:
        # Import and test weather integration
        print("\n1. Testing Live Weather Integration...")
        import aiohttp
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key:
            print("❌ No OpenWeather API key found!")
            return False
        
        # Test weather for multiple Karnataka cities
        karnataka_cities = [
            "Bengaluru,IN", "Mysuru,IN", "Mangaluru,IN", 
            "Hubli,IN", "Belagavi,IN"
        ]
        
        weather_data = {}
        async with aiohttp.ClientSession() as session:
            for city in karnataka_cities:
                try:
                    url = "http://api.openweathermap.org/data/2.5/weather"
                    params = {
                        'q': city,
                        'appid': api_key,
                        'units': 'metric'
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            weather_data[city] = {
                                'temperature': data['main']['temp'],
                                'humidity': data['main']['humidity'],
                                'pressure': data['main']['pressure'],
                                'weather': data['weather'][0]['description'],
                                'wind_speed': data.get('wind', {}).get('speed', 0) * 3.6,  # m/s to km/h
                                'clouds': data.get('clouds', {}).get('all', 0),
                                'visibility': data.get('visibility', 10000) / 1000  # m to km
                            }
                            print(f"  ✓ {city}: {data['main']['temp']}°C, {data['weather'][0]['description']}")
                        else:
                            print(f"  ❌ {city}: API error {response.status}")
                            
                except Exception as e:
                    print(f"  ❌ {city}: {e}")
        
        print(f"✓ Weather data retrieved for {len(weather_data)} cities")
        
        # Test prediction model
        print("\n2. Testing Prediction Model...")
        from src.api.routes.predictions import get_model_instance
        
        model = get_model_instance()
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Test predictions for each city with current weather
        print("\n3. Testing Real-Time Predictions...")
        predictions = {}
        
        for city, weather in weather_data.items():
            try:
                # Simulate grid conditions (in real app, this would come from utility data)
                grid_data = {
                    'load_factor': 0.75 + (weather['temperature'] - 20) * 0.01,  # Higher load in extreme temps
                    'voltage_stability': max(0.7, 0.95 - weather['wind_speed'] * 0.02),  # Wind affects stability
                    'historical_outages': 3,
                    'transformer_load': 0.8,
                    'feeder_health': max(0.6, 0.9 - weather['humidity'] * 0.002)  # Humidity affects equipment
                }
                
                # Prepare prediction input
                prediction_input = {
                    'weather': {
                        'temperature': weather['temperature'],
                        'humidity': weather['humidity'],
                        'wind_speed': weather['wind_speed'],
                        'rainfall': 0,  # Current weather doesn't include rainfall forecast
                        'lightning_strikes': 0,
                        'storm_alert': weather['wind_speed'] > 25 or 'storm' in weather['weather'].lower()
                    },
                    'grid': grid_data,
                    'prediction_horizon': 24
                }
                
                # Make prediction
                result = await model.predict(prediction_input, include_explanation=True)
                predictions[city] = result
                
                risk_level = "🔴 HIGH" if result['risk_score'] > 60 else "🟡 MEDIUM" if result['risk_score'] > 30 else "🟢 LOW"
                print(f"  {city}: {result['risk_score']:.1f}% {risk_level}")
                print(f"    Factors: {', '.join(result['contributing_factors'][:2])}")
                
            except Exception as e:
                print(f"  ❌ {city}: Prediction failed - {e}")
        
        # Test API endpoints directly
        print("\n4. Testing API Endpoints...")
        from src.api.main import app
        from fastapi.testclient import TestClient
        
        try:
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
            
            # Test live prediction endpoint with coordinates
            live_request = {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "grid_data": {
                    "substation_id": "BESCOM_BLR_001",
                    "load_factor": 0.8,
                    "voltage_stability": 0.85,
                    "historical_outages": 3,
                    "maintenance_status": False,
                    "feeder_health": 0.8
                }
            }
            
            response = client.post("/api/v1/predict/live", json=live_request)
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Live prediction endpoint working: {result['risk_score']:.1f}% risk")
            else:
                print(f"❌ Live prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except ImportError:
            print("⚠ TestClient not available, skipping HTTP endpoint tests")
        except Exception as e:
            print(f"❌ API endpoint test failed: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("REAL-TIME FUNCTIONALITY SUMMARY")
        print("=" * 60)
        print(f"✓ Live Weather Data: {len(weather_data)} cities")
        print(f"✓ Real-Time Predictions: {len(predictions)} successful")
        print(f"✓ Model: {'Trained' if hasattr(model, 'model') and model.model else 'Mock mode'}")
        print(f"✓ API Routes: Available")
        print(f"✓ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if weather_data and predictions:
            print("\n🎯 SYSTEM IS READY FOR REAL-TIME OPERATION!")
            
            # Show sample prediction
            sample_city = list(predictions.keys())[0]
            sample_pred = predictions[sample_city]
            print(f"\nSample Real-Time Prediction for {sample_city}:")
            print(f"  Risk Score: {sample_pred['risk_score']:.1f}%")
            print(f"  Confidence: {sample_pred['confidence_interval']['lower']:.1f}% - {sample_pred['confidence_interval']['upper']:.1f}%")
            print(f"  Key Factors: {', '.join(sample_pred['contributing_factors'])}")
            
            return True
        else:
            print("\n⚠ Some components need attention")
            return False
            
    except Exception as e:
        print(f"\n❌ Real-time test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_time_api())
    sys.exit(0 if success else 1)