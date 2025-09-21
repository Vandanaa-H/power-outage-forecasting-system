#!/usr/bin/env python3
"""
Simple FastAPI server for the Karnataka Power Outage Forecasting System
This server provides mock data and basic functionality for the frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import datetime
import random
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

app = FastAPI(
    title="Karnataka Power Outage Forecasting API",
    description="24-hour power outage prediction system for Karnataka, India",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.onrender.com",  # Render frontend
        "https://power-outage-forecasting-frontend.onrender.com"  # Your specific frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PredictionRequest(BaseModel):
    location: str
    hours_ahead: int = 24

class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: float
    wind_speed: float
    description: str

# Karnataka districts for mock data
KARNATAKA_DISTRICTS = [
    "Bangalore Urban", "Bangalore Rural", "Mysore", "Mandya", "Hassan",
    "Belgaum", "Hubli-Dharwad", "Bijapur", "Bagalkot", "Gulbarga",
    "Mangalore", "Udupi", "Shimoga", "Davangere", "Bellary"
]

def generate_mock_prediction(location: str) -> Dict[str, Any]:
    """Generate mock prediction data"""
    risk_levels = ["Low", "Medium", "High"]
    risk_level = random.choice(risk_levels)
    
    # Base probability on risk level
    if risk_level == "High":
        probability = random.uniform(0.6, 0.9)
    elif risk_level == "Medium":
        probability = random.uniform(0.3, 0.6)
    else:
        probability = random.uniform(0.1, 0.3)
    
    return {
        "location": location,
        "prediction_time": datetime.datetime.now().isoformat(),
        "risk_level": risk_level,
        "outage_probability": round(probability, 3),
        "confidence_score": round(random.uniform(0.8, 0.95), 3),
        "contributing_factors": random.sample([
            "High Temperature", "Strong Winds", "Heavy Rain", "Grid Load",
            "Maintenance Schedule", "Historical Patterns", "Seasonal Factors"
        ], random.randint(2, 4))
    }

def generate_mock_weather(location: str) -> Dict[str, Any]:
    """Generate mock weather data"""
    descriptions = ["Clear Sky", "Partly Cloudy", "Cloudy", "Light Rain", "Thunderstorm"]
    
    return {
        "location": location,
        "temperature": round(random.uniform(20, 35), 1),
        "humidity": random.randint(40, 80),
        "wind_speed": round(random.uniform(5, 25), 1),
        "pressure": random.randint(1000, 1020),
        "description": random.choice(descriptions),
        "feels_like": round(random.uniform(22, 38), 1),
        "visibility": random.randint(8, 15),
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Karnataka Power Outage Forecasting API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "warnings": 0,
        "uptime": "99.9%"
    }

@app.get("/api/predictions")
async def get_predictions(limit: int = 10, location: Optional[str] = None):
    """Get power outage predictions"""
    locations = [location] if location else random.sample(KARNATAKA_DISTRICTS, min(limit, len(KARNATAKA_DISTRICTS)))
    
    predictions = [generate_mock_prediction(loc) for loc in locations]
    
    return {
        "predictions": predictions,
        "total": len(predictions),
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/api/predictions")
async def create_prediction(request: PredictionRequest):
    """Create new prediction"""
    prediction = generate_mock_prediction(request.location)
    prediction["hours_ahead"] = request.hours_ahead
    return prediction

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """Get current weather data for a location"""
    weather_data = generate_mock_weather(location)
    return weather_data

@app.get("/api/weather")
async def get_weather_data(location: str = "Bangalore"):
    """Get current weather data"""
    weather_data = generate_mock_weather(location)
    return weather_data

@app.get("/api/analytics")
async def get_analytics():
    """Get system analytics"""
    return {
        "model_accuracy": round(random.uniform(0.92, 0.98), 3),
        "total_predictions": random.randint(1000, 5000),
        "active_alerts": random.randint(0, 10),
        "uptime": "99.9%",
        "performance_metrics": {
            "avg_response_time": round(random.uniform(0.8, 2.0), 2),
            "predictions_per_hour": random.randint(50, 200),
            "false_positive_rate": round(random.uniform(0.02, 0.08), 3)
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/advisories")
async def get_advisories(limit: int = 10):
    """Get public advisories"""
    severities = ["Critical", "High", "Medium", "Low", "Info"]
    advisories = []
    
    for i in range(min(limit, 5)):
        advisory = {
            "id": i + 1,
            "title": f"Weather Alert - {random.choice(KARNATAKA_DISTRICTS)}",
            "description": "Weather conditions may affect power infrastructure",
            "severity": random.choice(severities),
            "issued_at": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(hours=random.randint(6, 48))).isoformat(),
            "region": random.choice(KARNATAKA_DISTRICTS)
        }
        advisories.append(advisory)
    
    return {
        "advisories": advisories,
        "active_count": len([a for a in advisories if a["severity"] in ["Critical", "High"]]),
        "total": len(advisories)
    }

@app.get("/api/risk-metrics")
async def get_risk_metrics():
    """Get current risk metrics"""
    overall_risk = random.choice(["Low", "Medium", "High"])
    
    districts_risk = []
    for district in random.sample(KARNATAKA_DISTRICTS, 6):
        risk = random.choice(["Low", "Medium", "High"])
        score = random.randint(20, 90)
        districts_risk.append({
            "name": district,
            "risk": risk,
            "score": score
        })
    
    return {
        "overall_risk": overall_risk,
        "risk_score": random.randint(30, 85),
        "districts": districts_risk,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/recent-predictions")
async def get_recent_predictions(limit: int = 10):
    """Get recent predictions"""
    predictions = []
    
    for i in range(limit):
        prediction = generate_mock_prediction(random.choice(KARNATAKA_DISTRICTS))
        # Adjust timestamp to be in the past
        past_time = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(10, 180))
        prediction["prediction_time"] = past_time.isoformat()
        prediction["id"] = i + 1
        predictions.append(prediction)
    
    return predictions

@app.post("/api/what-if-simulation")
async def run_simulation(scenario: Dict[str, Any]):
    """Run what-if simulation"""
    # Mock simulation based on input parameters
    weather = scenario.get("weather", {})
    grid = scenario.get("grid", {})
    
    # Calculate mock probability based on scenario
    base_prob = 0.3
    
    # Weather factors
    temp = weather.get("temperature", 25)
    if temp > 35:
        base_prob += 0.2
    elif temp > 30:
        base_prob += 0.1
    
    wind = weather.get("windSpeed", 10)
    if wind > 30:
        base_prob += 0.15
    elif wind > 20:
        base_prob += 0.08
    
    # Grid factors
    load = grid.get("loadFactor", 75)
    if load > 90:
        base_prob += 0.2
    elif load > 80:
        base_prob += 0.1
    
    if grid.get("maintenanceScheduled", False):
        base_prob += 0.15
    
    # Ensure probability is between 0 and 1
    probability = min(max(base_prob, 0.05), 0.95)
    
    # Determine risk level
    if probability >= 0.7:
        risk_level = "High"
    elif probability >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return {
        "outage_probability": round(probability, 3),
        "risk_level": risk_level,
        "confidence_score": round(random.uniform(0.85, 0.95), 3),
        "contributing_factors": [
            {"factor": "Weather Conditions", "impact": round((temp - 25) * 0.01, 3)},
            {"factor": "Grid Load", "impact": round((load - 75) * 0.002, 3)},
            {"factor": "Wind Speed", "impact": round((wind - 10) * 0.005, 3)}
        ],
        "recommendations": [
            "Monitor weather conditions closely",
            "Ensure backup systems are ready",
            "Consider load balancing if necessary"
        ]
    }

@app.get("/api/system-health")
async def get_system_health():
    """Get system health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "warnings": 0,
        "services": {
            "api": "healthy",
            "database": "healthy",
            "weather_service": "healthy",
            "prediction_model": "healthy"
        }
    }

if __name__ == "__main__":
    print("🌟 Starting Karnataka Power Outage Forecasting API...")
    print("📍 Mock data server for frontend development")
    print("🔮 Simulating 24-hour outage predictions")
    print("🌐 API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
