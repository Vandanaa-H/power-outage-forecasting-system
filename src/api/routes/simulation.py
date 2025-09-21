from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from src.api.models import WhatIfRequest, WhatIfResponse, PredictionRequest, PredictionResponse
from src.models.ensemble_model import EnsemblePredictor
from src.utils.scenario_analyzer import ScenarioAnalyzer
# Simple in-memory cache to avoid Redis dependency issues
_simple_cache = {}

async def get_cache(key: str):
    """Simple cache getter."""
    return _simple_cache.get(key)

async def set_cache(key: str, value, ttl=None):
    """Simple cache setter."""
    _simple_cache[key] = value
    return True

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize components
ensemble_model = EnsemblePredictor()
scenario_analyzer = ScenarioAnalyzer()


async def get_ensemble_model():
    """Dependency to get the ensemble model."""
    return ensemble_model


async def get_scenario_analyzer():
    """Dependency to get the scenario analyzer."""
    return scenario_analyzer


@router.post("/what-if", response_model=WhatIfResponse)
async def run_what_if_simulation(
    request: WhatIfRequest,
    background_tasks: BackgroundTasks,
    model: EnsemblePredictor = Depends(get_ensemble_model),
    analyzer: ScenarioAnalyzer = Depends(get_scenario_analyzer)
):
    """
    Run what-if simulation to analyze impact of parameter changes.
    
    Compares baseline scenario with modified parameters to show risk changes.
    """
    try:
        # Generate simulation ID for tracking
        simulation_id = str(uuid.uuid4())
        
        # Generate cache key
        cache_key = f"whatif:{hash(str(request.dict()))}"
        
        # Check cache first
        cached_result = await get_cache(cache_key)
        if cached_result:
            logger.info("Returning cached what-if simulation")
            return WhatIfResponse(**cached_result)
        
        # Get baseline prediction
        baseline_input = {
            'weather': request.base_scenario.weather_data.dict(),
            'grid': request.base_scenario.grid_data.dict(),
            'prediction_horizon': request.base_scenario.prediction_horizon
        }
        
        baseline_result = await model.predict(baseline_input, include_explanation=False)
        
        # Create modified scenario by copying and applying changes
        modified_scenario_dict = request.base_scenario.dict()
        
        # Apply modifications to the dictionary
        for param_path, new_value in request.modified_parameters.items():
            try:
                # Navigate nested dictionary structure
                keys = param_path.split('.')
                current = modified_scenario_dict
                for key in keys[:-1]:
                    current = current[key]
                current[keys[-1]] = new_value
            except (KeyError, TypeError) as e:
                logger.warning(f"Failed to apply modification {param_path}={new_value}: {e}")
        
        # Get modified prediction
        modified_input = {
            'weather': modified_scenario_dict['weather_data'],
            'grid': modified_scenario_dict['grid_data'],
            'prediction_horizon': modified_scenario_dict['prediction_horizon']
        }
        
        modified_result = await model.predict(modified_input, include_explanation=True)
        
        # Analyze impact
        impact_analysis = await analyzer.analyze_impact(
            baseline_result, 
            modified_result, 
            request.modified_parameters
        )
        
        # Create response objects
        baseline_response = PredictionResponse(
            risk_score=baseline_result['risk_score'],
            confidence_interval=baseline_result['confidence_interval'],
            risk_level=_determine_risk_level(baseline_result['risk_score']),
            contributing_factors=baseline_result.get('contributing_factors', [])
        )
        
        modified_response = PredictionResponse(
            risk_score=modified_result['risk_score'],
            confidence_interval=modified_result['confidence_interval'],
            risk_level=_determine_risk_level(modified_result['risk_score']),
            explanation=modified_result.get('explanation'),
            contributing_factors=modified_result.get('contributing_factors', [])
        )
        
        # Calculate risk change
        risk_change = modified_result['risk_score'] - baseline_result['risk_score']
        
        # Create final response
        response = WhatIfResponse(
            scenario_name=request.scenario_name,
            base_prediction=baseline_response,
            modified_prediction=modified_response,
            risk_change=risk_change,
            impact_analysis=impact_analysis
        )
        
        # Cache the result for 10 minutes
        background_tasks.add_task(set_cache, cache_key, response.dict(), ttl=600)
        
        # Log simulation for analysis
        background_tasks.add_task(
            _log_simulation, 
            simulation_id, 
            request.dict(), 
            response.dict()
        )
        
        logger.info(f"What-if simulation completed: {simulation_id}, risk_change={risk_change}")
        return response
        
    except Exception as e:
        logger.error(f"What-if simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/what-if/batch")
async def run_batch_what_if_simulations(
    requests: List[WhatIfRequest],
    background_tasks: BackgroundTasks,
    model: EnsemblePredictor = Depends(get_ensemble_model),
    analyzer: ScenarioAnalyzer = Depends(get_scenario_analyzer)
):
    """
    Run multiple what-if simulations in batch.
    
    Useful for sensitivity analysis and parameter sweeps.
    """
    try:
        if len(requests) > 20:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size limited to 20 simulations")
        
        results = []
        
        for i, req in enumerate(requests):
            try:
                # Add batch index to scenario name
                if not req.scenario_name or req.scenario_name == "Custom Scenario":
                    req.scenario_name = f"Batch Scenario {i+1}"
                
                # Run individual simulation
                result = await run_what_if_simulation(
                    req, background_tasks, model, analyzer
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch simulation error for scenario {i}: {str(e)}")
                # Continue with other scenarios
                continue
        
        # Generate batch summary
        batch_summary = await analyzer.analyze_batch_results(results)
        
        return {
            "simulations": results,
            "batch_summary": batch_summary,
            "total_simulations": len(results),
            "successful_simulations": len(results)
        }
        
    except Exception as e:
        logger.error(f"Batch what-if simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch simulation failed: {str(e)}")


@router.get("/what-if/templates")
async def get_simulation_templates():
    """
    Get predefined simulation templates for common scenarios.
    
    Provides ready-to-use parameter modifications for typical analysis.
    """
    try:
        templates = {
            "severe_weather": {
                "name": "Severe Weather Impact",
                "description": "Simulate impact of severe weather conditions",
                "modifications": {
                    "weather_data.rainfall": 50.0,
                    "weather_data.wind_speed": 80.0,
                    "weather_data.storm_alert": True
                }
            },
            "high_demand": {
                "name": "High Demand Scenario",
                "description": "Simulate impact of increased electrical demand",
                "modifications": {
                    "grid_data.load_factor": 0.95,
                    "weather_data.temperature": 40.0
                }
            },
            "maintenance_impact": {
                "name": "Maintenance Impact",
                "description": "Simulate impact of grid maintenance",
                "modifications": {
                    "grid_data.maintenance_status": True,
                    "grid_data.feeder_health": 0.6
                }
            },
            "lightning_storm": {
                "name": "Lightning Storm",
                "description": "Simulate impact of lightning activity",
                "modifications": {
                    "weather_data.lightning_strikes": 15,
                    "weather_data.storm_alert": True,
                    "weather_data.rainfall": 25.0
                }
            },
            "grid_failure": {
                "name": "Grid Vulnerability",
                "description": "Simulate impact of grid vulnerabilities",
                "modifications": {
                    "grid_data.voltage_stability": 0.5,
                    "grid_data.feeder_health": 0.4
                }
            }
        }
        
        return {
            "templates": templates,
            "total_templates": len(templates),
            "usage_instructions": "Select a template and customize parameters as needed"
        }
        
    except Exception as e:
        logger.error(f"Simulation templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/what-if/sensitivity")
async def run_sensitivity_analysis(
    base_request: WhatIfRequest,
    parameter: str,
    min_value: float,
    max_value: float,
    background_tasks: BackgroundTasks,
    steps: int = 10,
    model = Depends(get_ensemble_model),
    analyzer = Depends(get_scenario_analyzer)
):
    """
    Run sensitivity analysis for a specific parameter.
    
    Varies one parameter across a range to understand its impact on risk.
    """
    try:
        if steps > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 steps allowed")
        
        if min_value >= max_value:
            raise HTTPException(status_code=400, detail="min_value must be less than max_value")
        
        # Generate parameter values
        step_size = (max_value - min_value) / (steps - 1)
        parameter_values = [min_value + i * step_size for i in range(steps)]
        
        results = []
        
        for value in parameter_values:
            try:
                # Create modified request
                modified_request = WhatIfRequest(
                    base_scenario=base_request.base_scenario,
                    modified_parameters={parameter: value},
                    scenario_name=f"Sensitivity {parameter}={value:.2f}"
                )
                
                # Run simulation
                result = await run_what_if_simulation(
                    modified_request, background_tasks, model, analyzer
                )
                
                results.append({
                    "parameter_value": value,
                    "risk_score": result.modified_prediction.risk_score,
                    "risk_change": result.risk_change,
                    "risk_level": result.modified_prediction.risk_level
                })
                
            except Exception as e:
                logger.error(f"Sensitivity analysis error for {parameter}={value}: {str(e)}")
                continue
        
        # Analyze sensitivity
        sensitivity_metrics = await analyzer.calculate_sensitivity_metrics(
            parameter, parameter_values, results
        )
        
        return {
            "parameter": parameter,
            "value_range": {"min": min_value, "max": max_value},
            "results": results,
            "sensitivity_metrics": sensitivity_metrics,
            "total_steps": len(results)
        }
        
    except Exception as e:
        logger.error(f"Sensitivity analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


async def _log_simulation(simulation_id: str, request_data: Dict, response_data: Dict):
    """Log simulation for analysis and auditing."""
    try:
        simulation_log = {
            "simulation_id": simulation_id,
            "timestamp": datetime.utcnow(),
            "request": request_data,
            "response": response_data
        }
        
        # In production, this would save to database
        logger.info(f"Simulation logged: {simulation_id}")
        
    except Exception as e:
        logger.error(f"Simulation logging error: {str(e)}")


def _determine_risk_level(risk_score: float):
    """Determine risk level based on risk score."""
    from src.api.models import RiskLevel
    
    if risk_score >= 80:
        return RiskLevel.CRITICAL
    elif risk_score >= 60:
        return RiskLevel.HIGH
    elif risk_score >= 30:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
