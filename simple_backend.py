#!/usr/bin/env python3
"""
Simple FastAPI backend for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from datetime import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Karnataka cities data
KARNATAKA_CITIES = [
    {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    {"name": "Mysore", "lat": 12.2958, "lon": 76.6394},
    {"name": "Hubli", "lat": 15.3647, "lon": 75.1240},
    {"name": "Mangalore", "lat": 12.9141, "lon": 74.8560},
    {"name": "Belgaum", "lat": 15.8497, "lon": 74.4977},
    {"name": "Gulbarga", "lat": 17.3297, "lon": 76.8343},
    {"name": "Davangere", "lat": 14.4644, "lon": 75.9237},
    {"name": "Bellary", "lat": 15.1394, "lon": 76.9214},
    {"name": "Bijapur", "lat": 16.8302, "lon": 75.7100},
    {"name": "Shimoga", "lat": 13.9299, "lon": 75.5681},
    {"name": "Tumkur", "lat": 13.3379, "lon": 77.1025},
    {"name": "Raichur", "lat": 16.2120, "lon": 77.3439}
]

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/weather/current")
async def get_current_weather(city: str = "Bangalore"):
    # Find city data
    city_data = next((c for c in KARNATAKA_CITIES if c["name"].lower() == city.lower()), KARNATAKA_CITIES[0])
    
    # Generate realistic weather data
    base_temp = 25
    if "coastal" in city.lower() or city.lower() in ["mangalore"]:
        base_temp = 32
    elif city.lower() in ["shimoga", "tumkur"]:
        base_temp = 28
    
    weather = {
        "location": city,
        "latitude": city_data["lat"],
        "longitude": city_data["lon"],
        "temperature": base_temp + random.randint(-5, 8),
        "description": random.choice(["Partly Cloudy", "Clear Sky", "Light Rain", "Overcast", "Sunny"]),
        "humidity": random.randint(45, 85),
        "wind_speed": random.randint(5, 25),
        "pressure": random.randint(1005, 1030),
        "feels_like": base_temp + random.randint(-3, 10),
        "visibility": random.randint(6, 14),
        "uv_index": random.randint(1, 8),
        "timestamp": datetime.now().isoformat()
    }
    
    return weather

@app.get("/api/v1/weather/cities")
async def get_cities():
    return {"cities": [city["name"] for city in KARNATAKA_CITIES]}

@app.get("/api/v1/advisories")
async def get_advisories(limit: int = 10):
    advisories = [
        {
            "id": "ADV001",
            "title": "High Wind Warning",
            "message": "Strong winds expected in coastal areas",
            "severity": "medium",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "ADV002", 
            "title": "Temperature Alert",
            "message": "High temperatures may affect electrical equipment",
            "severity": "low",
            "timestamp": datetime.now().isoformat()
        }
    ]
    return {"advisories": advisories[:limit], "active_count": len(advisories)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)