from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

from src.api.models import (
    PredictionRequest, PredictionResponse, RiskLevel
)
from src.models.ensemble_model import EnsemblePredictor
from src.utils.cache import get_cache, set_cache
from src.utils.monitoring import track_prediction_request

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the ensemble model (in production, this would be loaded from storage)
ensemble_model = EnsemblePredictor()


async def get_ensemble_model():
    """Dependency to get the ensemble model."""
    return ensemble_model


@router.post("/predict", response_model=PredictionResponse)
async def predict_outage(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    model: EnsemblePredictor = Depends(get_ensemble_model)
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
    model: EnsemblePredictor = Depends(get_ensemble_model)
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
