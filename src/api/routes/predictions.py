from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

from src.api.models import (
    PredictionRequest, PredictionResponse, RiskLevel, LivePredictionRequest
)
from src.models.ensemble_model import EnsemblePredictor
# Simple in-memory cache to avoid Redis dependency issues
_simple_cache = {}

async def get_cache(key: str):
    """Simple cache getter."""
    return _simple_cache.get(key)

async def set_cache(key: str, value, ttl=None):
    """Simple cache setter."""
    _simple_cache[key] = value
    return True

from src.utils.monitoring import track_prediction_request

logger = logging.getLogger(__name__)
router = APIRouter()

# Global model instance - will be loaded lazily
ensemble_model = None
model_loaded = False

def get_model_instance():
    """Get the model instance, loading it lazily if needed."""
    global ensemble_model, model_loaded
    
    if model_loaded:
        return ensemble_model
    
    try:
        import os
        import joblib
        import numpy as np
        
        # Try loading the pure sklearn model first
        sklearn_model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "karnataka_sklearn_model.joblib")
        sklearn_model_path = os.path.abspath(sklearn_model_path)
        
        if os.path.exists(sklearn_model_path):
            # Load the sklearn model package
            model_package = joblib.load(sklearn_model_path)
            
            # Create adapter for the sklearn model
            class SklearnModelAdapter:
                def __init__(self, model_package):
                    self.model = model_package['ensemble_model']
                    self.scaler = model_package['scaler'] 
                    self.feature_columns = model_package['feature_columns']
                    self.city_map = model_package['city_map']
                    self.escom_map = model_package['escom_map']
                    self.is_trained = True
                
                async def predict(self, input_data, include_explanation=True):
                    weather = input_data['weather']
                    grid = input_data['grid']
                    
                    # Map city if provided, default to Bengaluru
                    city_encoded = self.city_map.get('Bengaluru', 0)
                    escom_encoded = self.escom_map.get('BESCOM', 0)
                    
                    # Prepare features matching training format
                    features = [
                        weather.get('temperature', 25),
                        weather.get('humidity', 60),
                        weather.get('wind_speed', 10),
                        weather.get('rainfall', 0),
                        weather.get('lightning_strikes', 0),
                        1 if weather.get('storm_alert', False) else 0,
                        grid.get('load_factor', 0.7),
                        grid.get('voltage_stability', 0.9),
                        12,  # hour_of_day default
                        0,   # day_of_week default  
                        9,   # month default
                        2,   # season default
                        grid.get('historical_outages', 2),
                        grid.get('feeder_health', 0.8),
                        grid.get('transformer_load', 0.7),
                        grid.get('population', 10000000),
                        grid.get('priority_tier', 1),
                        1,   # is_monsoon default
                        0,   # is_summer default
                        city_encoded,
                        escom_encoded
                    ]
                    
                    # Scale features and predict
                    features_scaled = self.scaler.transform([features])
                    proba = self.model.predict_proba(features_scaled)[0][1] * 100
                    
                    return {
                        'risk_score': float(proba),
                        'confidence_interval': {'lower': max(0, proba-10), 'upper': min(100, proba+10)},
                        'contributing_factors': self._get_factors(weather, grid, proba)
                    }
                
                def _get_factors(self, weather, grid, risk_score):
                    factors = []
                    if weather.get('rainfall', 0) > 25:
                        factors.append("Heavy rainfall expected")
                    if weather.get('storm_alert', False):
                        factors.append("Active storm warning")
                    if grid.get('voltage_stability', 1) < 0.7:
                        factors.append("Grid voltage instability")
                    if grid.get('load_factor', 0) > 0.8:
                        factors.append("High electrical demand")
                    if weather.get('lightning_strikes', 0) > 5:
                        factors.append("Lightning activity detected")
                    if not factors:
                        factors.append(f"Normal conditions (Score: {risk_score:.1f}%)")
                    return factors
            
            ensemble_model = SklearnModelAdapter(model_package)
            logger.info(f"Loaded sklearn model package from {sklearn_model_path}")
            logger.info(f"Model accuracy: {model_package['model_info']['accuracy']:.3f}")
        else:
            # Fallback to original ensemble model
            ensemble_model = EnsemblePredictor()
            default_model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "karnataka_trained")
            default_model_dir = os.path.abspath(default_model_dir)
            if os.path.isdir(default_model_dir):
                ensemble_model.load_model(default_model_dir)
                logger.info(f"Loaded trained models from {default_model_dir}")
            else:
                logger.warning("No trained models found; using mock prediction.")
        
        model_loaded = True
    except Exception as e:
        logger.warning(f"Model load failed, falling back to mock: {e}")
        ensemble_model = EnsemblePredictor()  # Use original model in mock mode
        model_loaded = True
    
    return ensemble_model


async def get_ensemble_model():
    """Dependency to get the ensemble model."""
    return get_model_instance()


@router.post("/predict", response_model=PredictionResponse)
async def predict_outage(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    model = Depends(get_ensemble_model)
):
    """
    Predict power outage risk for the next 24 hours.
    
    Returns risk score, confidence intervals, and explanations.
    """
    try:
        # Track the request for monitoring
        background_tasks.add_task(track_prediction_request, request)
        
        # Generate cache key
        cache_key = f"prediction:{hash(str(request.dict()))}"
        
        # Check cache first
        cached_result = await get_cache(cache_key)
        if cached_result:
            logger.info("Returning cached prediction result")
            return PredictionResponse(**cached_result)
        
        # Prepare input data
        input_data = {
            'weather': request.weather_data.dict(),
            'grid': request.grid_data.dict(),
            'prediction_horizon': request.prediction_horizon
        }
        
        # Make prediction
        prediction_result = await model.predict(
            input_data, 
            include_explanation=request.include_explanation
        )

        # Enrich explanation with top features if SHAP data is present
        try:
            expl = prediction_result.get('explanation') if isinstance(prediction_result, dict) else None
            if expl and isinstance(expl, dict):
                shap_vals = expl.get('shap_values')
                if isinstance(shap_vals, dict) and shap_vals:
                    # Sort by absolute impact and take top 5
                    top = sorted(shap_vals.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]
                    expl['top_features'] = [
                        { 'feature': k, 'impact': float(v) } for k, v in top
                    ]
                    prediction_result['explanation'] = expl
        except Exception as _:
            pass
        
        # Determine risk level
        risk_level = _determine_risk_level(prediction_result['risk_score'])
        
        # Create response
        response = PredictionResponse(
            risk_score=prediction_result['risk_score'],
            confidence_interval=prediction_result['confidence_interval'],
            risk_level=risk_level,
            explanation=prediction_result.get('explanation'),
            contributing_factors=prediction_result.get('contributing_factors', [])
        )
        
        # Cache the result for 5 minutes
        background_tasks.add_task(set_cache, cache_key, response.dict(), ttl=300)
        
        logger.info(f"Prediction completed: risk_score={response.risk_score}, level={risk_level}")
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch_outages(
    requests: List[PredictionRequest],
    background_tasks: BackgroundTasks,
    model = Depends(get_ensemble_model)
):
    """
    Predict power outage risks for multiple locations/scenarios.
    
    Useful for generating heatmap data or bulk predictions.
    """
    try:
        if len(requests) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size limited to 100 requests")
        
        results = []
        
        for req in requests:
            try:
                # Prepare input data
                input_data = {
                    'weather': req.weather_data.dict(),
                    'grid': req.grid_data.dict(),
                    'prediction_horizon': req.prediction_horizon
                }
                
                # Make prediction
                prediction_result = await model.predict(
                    input_data, 
                    include_explanation=req.include_explanation
                )
                
                # Determine risk level
                risk_level = _determine_risk_level(prediction_result['risk_score'])
                
                # Create response
                response = PredictionResponse(
                    risk_score=prediction_result['risk_score'],
                    confidence_interval=prediction_result['confidence_interval'],
                    risk_level=risk_level,
                    explanation=prediction_result.get('explanation'),
                    contributing_factors=prediction_result.get('contributing_factors', [])
                )
                
                results.append(response)
                
            except Exception as e:
                logger.error(f"Batch prediction error for request: {str(e)}")
                # Add a default error response
                results.append(PredictionResponse(
                    risk_score=0.0,
                    confidence_interval={'lower': 0.0, 'upper': 0.0},
                    risk_level=RiskLevel.LOW,
                    contributing_factors=["Prediction failed"]
                ))
        
        # Track batch request
        background_tasks.add_task(track_prediction_request, {"batch_size": len(requests)})
        
        logger.info(f"Batch prediction completed: {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get("/predict/historical")
async def get_historical_predictions(
    latitude: float,
    longitude: float,
    start_date: datetime,
    end_date: datetime,
    limit: int = 100
):
    """
    Get historical predictions for a specific location.
    
    Useful for model performance analysis and trend visualization.
    """
    try:
        # Validate date range
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if (end_date - start_date).days > 30:
            raise HTTPException(status_code=400, detail="Date range limited to 30 days")
        
        # This would query from database in production
        # For now, return mock data structure
        historical_data = {
            "location": {"latitude": latitude, "longitude": longitude},
            "date_range": {"start": start_date, "end": end_date},
            "predictions": [],  # Would be populated from database
            "statistics": {
                "total_predictions": 0,
                "average_risk_score": 0.0,
                "accuracy_metrics": {}
            }
        }
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Historical predictions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical predictions: {str(e)}")


def _determine_risk_level(risk_score: float) -> RiskLevel:
    """Determine risk level based on risk score."""
    if risk_score >= 80:
        return RiskLevel.CRITICAL
    elif risk_score >= 60:
        return RiskLevel.HIGH
    elif risk_score >= 30:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


@router.post("/predict/live", response_model=PredictionResponse)
async def predict_outage_live(
    request: LivePredictionRequest,
    background_tasks: BackgroundTasks,
    model = Depends(get_ensemble_model)
):
    """
    Predict power outage risk using live weather for a city or coordinates.
    If grid_data not provided, apply sensible defaults.
    """
    try:
        # Resolve location
        lat, lon = None, None
        city_key = None
        if request.city:
            city_key = request.city.strip().lower()
        if request.latitude is not None and request.longitude is not None:
            lat, lon = float(request.latitude), float(request.longitude)

        # Fetch live weather
        from src.weather.karnataka_weather_api import KarnatakaWeatherAPI
        from config.settings import settings
        weather_api = KarnatakaWeatherAPI(
            openweather_api_key=settings.openweather_api_key,
            weatherapi_key=settings.weatherapi_key if hasattr(settings, 'weatherapi_key') else None
        )

        if city_key and city_key in weather_api.karnataka_cities:
            coords = weather_api.karnataka_cities[city_key]
            lat, lon = coords['lat'], coords['lon']
        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail="Unknown city or missing coordinates")

        current = await weather_api.get_openweather_current(city_key or "custom", lat, lon)
        if not current:
            raise HTTPException(status_code=502, detail="Failed to fetch live weather")

        weather_features = weather_api.weather_data_to_ml_features(current)

        # Grid defaults if not provided
        grid = request.grid_data.dict() if request.grid_data else {
            'substation_id': f"auto-{city_key or 'custom'}",
            'load_factor': 0.7,
            'voltage_stability': 0.9,
            'historical_outages': 2,
            'maintenance_status': False,
            'feeder_health': 0.8
        }

        # Prepare and predict
        input_data = {
            'weather': weather_features,
            'grid': grid,
            'prediction_horizon': 24
        }

        prediction_result = await model.predict(
            input_data,
            include_explanation=request.include_explanation
        )

        risk_level = _determine_risk_level(prediction_result['risk_score'])

        response = PredictionResponse(
            risk_score=prediction_result['risk_score'],
            confidence_interval=prediction_result['confidence_interval'],
            risk_level=risk_level,
            explanation=prediction_result.get('explanation'),
            contributing_factors=prediction_result.get('contributing_factors', [])
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Live prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Live prediction failed: {str(e)}")
