from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WeatherInput(BaseModel):
    """Weather data input model."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    lightning_strikes: int = Field(0, ge=0, description="Lightning strikes count")
    storm_alert: bool = Field(False, description="Storm alert status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GridInput(BaseModel):
    """Power grid data input model."""
    substation_id: str = Field(..., description="Substation identifier")
    load_factor: float = Field(..., ge=0, le=1, description="Current load factor")
    voltage_stability: float = Field(..., ge=0, le=1, description="Voltage stability index")
    historical_outages: int = Field(0, ge=0, description="Historical outage count")
    maintenance_status: bool = Field(False, description="Under maintenance status")
    feeder_health: float = Field(..., ge=0, le=1, description="Feeder health score")


class PredictionRequest(BaseModel):
    """Outage prediction request model."""
    weather_data: WeatherInput
    grid_data: GridInput
    prediction_horizon: int = Field(24, ge=1, le=72, description="Prediction horizon in hours")
    include_explanation: bool = Field(True, description="Include SHAP explanations")


class PredictionResponse(BaseModel):
    """Outage prediction response model."""
    risk_score: float = Field(..., ge=0, le=100, description="Outage risk score (0-100)")
    confidence_interval: Dict[str, float] = Field(..., description="Confidence intervals")
    risk_level: RiskLevel = Field(..., description="Risk level category")
    prediction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    explanation: Optional[Dict[str, Any]] = Field(None, description="SHAP explanation data")
    contributing_factors: List[str] = Field(default_factory=list, description="Main risk factors")


class HeatmapPoint(BaseModel):
    """Heatmap data point model."""
    latitude: float
    longitude: float
    risk_score: float
    region_name: str
    population_affected: Optional[int] = None


class HeatmapResponse(BaseModel):
    """Heatmap response model."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_points: List[HeatmapPoint]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Advisory(BaseModel):
    """Advisory message model."""
    id: str = Field(..., description="Advisory identifier")
    title: str = Field(..., description="Advisory title")
    message: str = Field(..., description="Advisory message")
    severity: RiskLevel = Field(..., description="Advisory severity")
    affected_areas: List[str] = Field(default_factory=list)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(..., description="Advisory expiration time")
    recommendations: List[str] = Field(default_factory=list)


class AdvisoryResponse(BaseModel):
    """Advisory response model."""
    advisories: List[Advisory]
    total_count: int
    active_count: int


class WhatIfRequest(BaseModel):
    """What-if simulation request model."""
    base_scenario: PredictionRequest
    modified_parameters: Dict[str, Any] = Field(..., description="Parameters to modify")
    scenario_name: str = Field("Custom Scenario", description="Scenario name")


class WhatIfResponse(BaseModel):
    """What-if simulation response model."""
    scenario_name: str
    base_prediction: PredictionResponse
    modified_prediction: PredictionResponse
    risk_change: float = Field(..., description="Change in risk score")
    impact_analysis: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    app_name: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# Validation models for geospatial data
class GeoPoint(BaseModel):
    """Geographic point model."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class BoundingBox(BaseModel):
    """Geographic bounding box model."""
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)
    
    @validator('north')
    def validate_north_south(cls, v, values):
        if 'south' in values and v <= values['south']:
            raise ValueError('North must be greater than south')
        return v
    
    @validator('east')
    def validate_east_west(cls, v, values):
        if 'west' in values and v <= values['west']:
            raise ValueError('East must be greater than west')
        return v
