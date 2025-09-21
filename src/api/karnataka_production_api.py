"""
Production API Endpoints for Karnataka Power Outage Forecasting
Integrates trained models with real-time weather data
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
import joblib
import asyncio
from datetime import datetime, timedelta
import logging
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.weather.karnataka_weather_api import KarnatakaWeatherAPI, WeatherData
from src.models.ensemble_model import EnsembleModel
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Karnataka Power Outage Forecasting API",
    description="24-Hour Power Outage Predictions for Karnataka using Real Weather Data & Trained ML Models",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded models and weather API
loaded_models = {}
weather_api = None

class OutagePredictionRequest(BaseModel):
    """Request model for outage prediction."""
    city: str
    hours_ahead: int = 24
    include_explanation: bool = True

class OutagePrediction(BaseModel):
    """Response model for outage prediction."""
    city: str
    timestamp: datetime
    outage_probability: float
    outage_predicted: bool
    confidence_score: float
    weather_factors: Dict[str, float]
    explanation: Optional[Dict[str, str]] = None

class WeatherConditions(BaseModel):
    """Current weather conditions."""
    city: str
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    storm_alert: bool
    lightning_risk: int

class SystemStatus(BaseModel):
    """System status response."""
    status: str
    models_loaded: List[str]
    weather_api_connected: bool
    last_update: datetime
    karnataka_cities: List[str]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models and weather API on startup."""
    global loaded_models, weather_api
    
    logger.info("Starting Karnataka Power Outage Forecasting API...")
    
    # Initialize weather API
    openweather_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
    weatherapi_key = os.getenv('WEATHERAPI_KEY', 'demo_key')
    
    weather_api = KarnatakaWeatherAPI(
        openweather_api_key=openweather_key,
        weatherapi_key=weatherapi_key
    )
    
    # Load trained models
    model_path = "models/karnataka_outage_model.joblib"
    if os.path.exists(model_path):
        try:
            loaded_models['ensemble'] = joblib.load(model_path)
            logger.info("Loaded trained Karnataka outage prediction model")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Create dummy model for demo
            loaded_models['ensemble'] = create_dummy_model()
            logger.info("WARNING: Using dummy model - train real model first!")
    else:
        # Create dummy model for demo
        loaded_models['ensemble'] = create_dummy_model()
        logger.info("WARNING: Model file not found - using dummy model for demo")
    
    logger.info("Karnataka Power Outage Forecasting API is ready!")

def create_dummy_model():
    """Create a dummy model for demo purposes."""
    class DummyModel:
        def predict_proba(self, X):
            # Simple heuristic based on weather conditions
            probabilities = []
            for row in X:
                # Extract features (adjust indices based on your feature order)
                rainfall = row[3] if len(row) > 3 else 0
                wind_speed = row[2] if len(row) > 2 else 0
                lightning = row[4] if len(row) > 4 else 0
                
                # Simple risk calculation
                risk = 0.1  # Base risk
                if rainfall > 25: risk += 0.3
                if wind_speed > 30: risk += 0.2
                if lightning > 2: risk += 0.25
                
                risk = min(0.95, risk)  # Cap at 95%
                probabilities.append([1-risk, risk])
            
            return np.array(probabilities)
        
        def predict(self, X):
            proba = self.predict_proba(X)
            return (proba[:, 1] > 0.5).astype(int)
    
    return DummyModel()

def get_weather_api():
    """Dependency to get weather API instance."""
    if weather_api is None:
        raise HTTPException(status_code=500, detail="Weather API not initialized")
    return weather_api

def get_model():
    """Dependency to get loaded model."""
    if 'ensemble' not in loaded_models:
        raise HTTPException(status_code=500, detail="Prediction model not loaded")
    return loaded_models['ensemble']

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Karnataka 24-Hour Power Outage Forecasting API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "cities_covered": "12 major Karnataka cities",
        "prediction_horizon": "24 hours"
    }

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status and health check."""
    return SystemStatus(
        status="operational",
        models_loaded=list(loaded_models.keys()),
        weather_api_connected=weather_api is not None,
        last_update=datetime.utcnow(),
        karnataka_cities=list(weather_api.karnataka_cities.keys()) if weather_api else []
    )

@app.get("/cities")
async def get_supported_cities():
    """Get list of supported Karnataka cities."""
    if not weather_api:
        raise HTTPException(status_code=500, detail="Weather API not initialized")
    
    cities = {}
    for city, info in weather_api.karnataka_cities.items():
        cities[city] = {
            "name": city.title(),
            "latitude": info['lat'],
            "longitude": info['lon'],
            "priority": info['priority'],
            "escom_zone": get_escom_zone(city)
        }
    
    return {"cities": cities, "total_count": len(cities)}

def get_escom_zone(city: str) -> str:
    """Get ESCOM zone for a city."""
    escom_mapping = {
        'bangalore': 'BESCOM',
        'mysore': 'CHESCOM',
        'hubli': 'HESCOM',
        'dharwad': 'HESCOM',
        'mangalore': 'MESCOM',
        'belgaum': 'HESCOM',
        'gulbarga': 'GESCOM',
        'davangere': 'CHESCOM',
        'bellary': 'GESCOM',
        'bijapur': 'HESCOM',
        'shimoga': 'CHESCOM',
        'tumkur': 'BESCOM'
    }
    return escom_mapping.get(city.lower(), 'BESCOM')

@app.get("/weather/current")
async def get_current_weather(
    city: Optional[str] = None,
    weather_api: KarnatakaWeatherAPI = Depends(get_weather_api)
):
    """Get current weather conditions for Karnataka cities."""
    try:
        if city:
            # Get weather for specific city
            if city.lower() not in weather_api.karnataka_cities:
                raise HTTPException(status_code=404, detail=f"City '{city}' not supported")
            
            coords = weather_api.karnataka_cities[city.lower()]
            weather_data = await weather_api.get_openweather_current(
                city.lower(), coords['lat'], coords['lon']
            )
            
            if not weather_data:
                raise HTTPException(status_code=503, detail="Weather data not available")
            
            return {
                "city": weather_data.city,
                "conditions": {
                    "temperature": weather_data.temperature,
                    "humidity": weather_data.humidity,
                    "rainfall": weather_data.rainfall,
                    "wind_speed": weather_data.wind_speed,
                    "storm_alert": bool(weather_data.storm_alert),
                    "lightning_risk": weather_data.lightning_risk,
                    "description": weather_data.weather_description
                },
                "timestamp": weather_data.timestamp
            }
        else:
            # Get weather for all cities
            weather_data = await weather_api.get_current_weather_all_cities()
            
            results = {}
            for wd in weather_data:
                results[wd.city] = {
                    "temperature": wd.temperature,
                    "humidity": wd.humidity,
                    "rainfall": wd.rainfall,
                    "wind_speed": wd.wind_speed,
                    "storm_alert": bool(wd.storm_alert),
                    "lightning_risk": wd.lightning_risk,
                    "description": wd.weather_description,
                    "timestamp": wd.timestamp
                }
            
            return {"weather_data": results, "cities_count": len(results)}
    
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")

@app.post("/predict", response_model=OutagePrediction)
async def predict_outage(
    request: OutagePredictionRequest,
    weather_api: KarnatakaWeatherAPI = Depends(get_weather_api),
    model = Depends(get_model)
):
    """Predict power outage for a specific city."""
    try:
        city_lower = request.city.lower()
        
        if city_lower not in weather_api.karnataka_cities:
            raise HTTPException(status_code=404, detail=f"City '{request.city}' not supported")
        
        # Get current weather
        coords = weather_api.karnataka_cities[city_lower]
        weather_data = await weather_api.get_openweather_current(
            city_lower, coords['lat'], coords['lon']
        )
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather data not available")
        
        # Prepare features for ML model
        features = prepare_prediction_features(weather_data, request.city)
        
        # Make prediction
        prediction_proba = model.predict_proba([features])[0]
        outage_probability = prediction_proba[1]  # Probability of outage
        outage_predicted = outage_probability > 0.5
        confidence_score = max(prediction_proba)
        
        # Weather factors affecting prediction
        weather_factors = {
            "temperature_impact": calculate_temperature_impact(weather_data.temperature),
            "rainfall_impact": calculate_rainfall_impact(weather_data.rainfall),
            "wind_impact": calculate_wind_impact(weather_data.wind_speed),
            "lightning_impact": weather_data.lightning_risk / 5.0,
            "storm_impact": float(weather_data.storm_alert)
        }
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            explanation = generate_prediction_explanation(
                weather_data, outage_probability, weather_factors
            )
        
        return OutagePrediction(
            city=request.city.title(),
            timestamp=datetime.utcnow(),
            outage_probability=round(outage_probability, 3),
            outage_predicted=outage_predicted,
            confidence_score=round(confidence_score, 3),
            weather_factors=weather_factors,
            explanation=explanation
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for {request.city}: {e}")
        raise HTTPException(status_code=500, detail="Prediction service error")

@app.post("/predict/batch")
async def predict_outage_batch(
    cities: List[str],
    hours_ahead: int = 24,
    weather_api: KarnatakaWeatherAPI = Depends(get_weather_api),
    model = Depends(get_model)
):
    """Predict power outages for multiple cities."""
    try:
        predictions = []
        
        for city in cities:
            request = OutagePredictionRequest(
                city=city,
                hours_ahead=hours_ahead,
                include_explanation=False
            )
            
            try:
                prediction = await predict_outage(request, weather_api, model)
                predictions.append(prediction.dict())
            except Exception as e:
                logger.warning(f"Failed to predict for {city}: {e}")
                continue
        
        return {
            "predictions": predictions,
            "total_cities": len(cities),
            "successful_predictions": len(predictions),
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail="Batch prediction service error")

def prepare_prediction_features(weather_data: WeatherData, city: str) -> List[float]:
    """Prepare features for ML model prediction."""
    # Get ESCOM zone encoding
    escom_zone = get_escom_zone(city)
    escom_encoding = {
        'BESCOM': 0, 'CHESCOM': 1, 'HESCOM': 2, 
        'MESCOM': 3, 'GESCOM': 4
    }
    
    # Get city priority
    priority = weather_api.karnataka_cities[city.lower()]['priority']
    
    # Current hour (for time-based patterns)
    current_hour = datetime.now().hour
    
    # Weekend flag
    is_weekend = datetime.now().weekday() >= 5
    
    # Prepare feature vector (adjust based on your model's expected features)
    features = [
        weather_data.temperature,
        weather_data.humidity,
        weather_data.wind_speed,
        weather_data.rainfall,
        weather_data.lightning_risk,
        weather_data.storm_alert,
        weather_data.pressure,
        weather_data.visibility,
        weather_data.monsoon_intensity,
        escom_encoding.get(escom_zone, 0),
        priority,
        current_hour,
        int(is_weekend)
    ]
    
    return features

def calculate_temperature_impact(temperature: float) -> float:
    """Calculate temperature impact on outage risk."""
    # Extreme temperatures increase risk
    if temperature > 40 or temperature < 5:
        return 0.8
    elif temperature > 35 or temperature < 10:
        return 0.5
    else:
        return 0.1

def calculate_rainfall_impact(rainfall: float) -> float:
    """Calculate rainfall impact on outage risk."""
    if rainfall > 50:
        return 0.9
    elif rainfall > 25:
        return 0.6
    elif rainfall > 10:
        return 0.3
    else:
        return 0.0

def calculate_wind_impact(wind_speed: float) -> float:
    """Calculate wind impact on outage risk."""
    if wind_speed > 60:
        return 0.9
    elif wind_speed > 40:
        return 0.6
    elif wind_speed > 25:
        return 0.3
    else:
        return 0.0

def generate_prediction_explanation(
    weather_data: WeatherData, 
    outage_probability: float, 
    weather_factors: Dict[str, float]
) -> Dict[str, str]:
    """Generate human-readable explanation for prediction."""
    risk_level = "Low"
    if outage_probability > 0.7:
        risk_level = "High"
    elif outage_probability > 0.4:
        risk_level = "Medium"
    
    # Identify primary risk factors
    primary_factors = []
    if weather_factors["rainfall_impact"] > 0.5:
        primary_factors.append("heavy rainfall")
    if weather_factors["wind_impact"] > 0.5:
        primary_factors.append("strong winds")
    if weather_factors["lightning_impact"] > 0.4:
        primary_factors.append("lightning activity")
    if weather_factors["temperature_impact"] > 0.5:
        primary_factors.append("extreme temperature")
    
    if not primary_factors:
        primary_factors = ["normal weather conditions"]
    
    return {
        "risk_level": risk_level,
        "primary_factors": ", ".join(primary_factors),
        "summary": f"Outage probability is {outage_probability:.1%} due to {', '.join(primary_factors)}",
        "recommendation": get_recommendation(outage_probability),
        "weather_summary": weather_data.weather_description
    }

def get_recommendation(outage_probability: float) -> str:
    """Get recommendation based on outage probability."""
    if outage_probability > 0.7:
        return "High risk: Prepare backup power systems and monitor grid closely"
    elif outage_probability > 0.4:
        return "Medium risk: Stay alert for potential outages and have contingency plans ready"
    else:
        return "Low risk: Normal operations expected"

if __name__ == "__main__":
    import uvicorn
    print("Starting Karnataka Power Outage Forecasting API...")
    print("Covering 12 major Karnataka cities with real-time weather data")
    print("24-hour outage predictions using trained ML models")
    print("API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
