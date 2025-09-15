from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import geojson

from src.api.models import HeatmapResponse, HeatmapPoint, BoundingBox
from src.utils.geospatial import GeoSpatialProcessor
from src.utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize geospatial processor
geo_processor = GeoSpatialProcessor()


async def get_geo_processor():
    """Dependency to get the geospatial processor."""
    return geo_processor


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_risk_heatmap(
    north: float = Query(..., ge=-90, le=90, description="Northern boundary"),
    south: float = Query(..., ge=-90, le=90, description="Southern boundary"),
    east: float = Query(..., ge=-180, le=180, description="Eastern boundary"),
    west: float = Query(..., ge=-180, le=180, description="Western boundary"),
    resolution: int = Query(50, ge=10, le=200, description="Grid resolution"),
    prediction_horizon: int = Query(24, ge=1, le=72, description="Prediction horizon in hours"),
    geo_proc: GeoSpatialProcessor = Depends(get_geo_processor)
):
    """
    Generate risk heatmap data for the specified geographic area.
    
    Returns GeoJSON-compatible data for map visualization.
    """
    try:
        # Validate bounding box
        if north <= south:
            raise HTTPException(status_code=400, detail="North must be greater than south")
        if east <= west:
            raise HTTPException(status_code=400, detail="East must be greater than west")
        
        # Create bounding box
        bbox = BoundingBox(north=north, south=south, east=east, west=west)
        
        # Generate cache key
        cache_key = f"heatmap:{hash(str(bbox.dict()))}:{resolution}:{prediction_horizon}"
        
        # Check cache first
        cached_result = await get_cache(cache_key)
        if cached_result:
            logger.info("Returning cached heatmap data")
            return HeatmapResponse(**cached_result)
        
        # Generate grid points
        grid_points = await geo_proc.generate_grid_points(bbox, resolution)
        
        # Get risk predictions for each grid point
        heatmap_points = []
        for point in grid_points:
            try:
                # This would use the prediction model in production
                risk_score = await _get_risk_for_location(
                    point['latitude'], 
                    point['longitude'], 
                    prediction_horizon
                )
                
                heatmap_point = HeatmapPoint(
                    latitude=point['latitude'],
                    longitude=point['longitude'],
                    risk_score=risk_score,
                    region_name=point.get('region_name', 'Unknown'),
                    population_affected=point.get('population', None)
                )
                
                heatmap_points.append(heatmap_point)
                
            except Exception as e:
                logger.warning(f"Failed to get risk for point {point}: {str(e)}")
                continue
        
        # Create response
        response = HeatmapResponse(
            data_points=heatmap_points,
            metadata={
                'bounding_box': bbox.dict(),
                'resolution': resolution,
                'prediction_horizon': prediction_horizon,
                'total_points': len(heatmap_points)
            }
        )
        
        # Cache for 10 minutes
        await set_cache(cache_key, response.dict(), ttl=600)
        
        logger.info(f"Heatmap generated: {len(heatmap_points)} points")
        return response
        
    except Exception as e:
        logger.error(f"Heatmap generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@router.get("/heatmap/geojson")
async def get_risk_heatmap_geojson(
    north: float = Query(..., ge=-90, le=90),
    south: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    west: float = Query(..., ge=-180, le=180),
    resolution: int = Query(50, ge=10, le=200),
    prediction_horizon: int = Query(24, ge=1, le=72),
    geo_proc: GeoSpatialProcessor = Depends(get_geo_processor)
):
    """
    Generate risk heatmap as GeoJSON for direct map integration.
    
    Returns standard GeoJSON format for web mapping libraries.
    """
    try:
        # Get heatmap data
        heatmap_data = await get_risk_heatmap(
            north=north, south=south, east=east, west=west,
            resolution=resolution, prediction_horizon=prediction_horizon,
            geo_proc=geo_proc
        )
        
        # Convert to GeoJSON
        features = []
        for point in heatmap_data.data_points:
            feature = geojson.Feature(
                geometry=geojson.Point((point.longitude, point.latitude)),
                properties={
                    'risk_score': point.risk_score,
                    'region_name': point.region_name,
                    'population_affected': point.population_affected,
                    'risk_level': _get_risk_level_string(point.risk_score)
                }
            )
            features.append(feature)
        
        # Create feature collection
        feature_collection = geojson.FeatureCollection(
            features=features,
            properties={
                'timestamp': heatmap_data.timestamp.isoformat(),
                'metadata': heatmap_data.metadata
            }
        )
        
        return feature_collection
        
    except Exception as e:
        logger.error(f"GeoJSON heatmap generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GeoJSON generation failed: {str(e)}")


@router.get("/heatmap/regions")
async def get_regional_risk_summary(
    region_type: str = Query("district", description="Region type: district, state, or city"),
    geo_proc: GeoSpatialProcessor = Depends(get_geo_processor)
):
    """
    Get risk summary aggregated by administrative regions.
    
    Useful for high-level dashboard views and alerts.
    """
    try:
        # This would query actual regional data in production
        regional_data = await geo_proc.get_regional_risk_summary(region_type)
        
        return {
            "region_type": region_type,
            "timestamp": datetime.utcnow(),
            "regions": regional_data,
            "summary": {
                "total_regions": len(regional_data),
                "high_risk_regions": len([r for r in regional_data if r.get('risk_score', 0) >= 60]),
                "average_risk": sum(r.get('risk_score', 0) for r in regional_data) / len(regional_data) if regional_data else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Regional risk summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regional summary failed: {str(e)}")


@router.get("/heatmap/live")
async def get_live_risk_updates(
    geo_proc: GeoSpatialProcessor = Depends(get_geo_processor)
):
    """
    Get live risk updates for real-time monitoring.
    
    Returns recently updated risk assessments.
    """
    try:
        # This would stream real-time updates in production
        live_updates = await geo_proc.get_live_risk_updates()
        
        return {
            "timestamp": datetime.utcnow(),
            "updates": live_updates,
            "total_updates": len(live_updates),
            "refresh_interval": 60  # seconds
        }
        
    except Exception as e:
        logger.error(f"Live risk updates error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Live updates failed: {str(e)}")


async def _get_risk_for_location(latitude: float, longitude: float, horizon: int) -> float:
    """Get risk score for a specific location."""
    # This would use the actual prediction model
    # For now, return a mock risk score based on location
    import random
    random.seed(int(latitude * 1000 + longitude * 1000))  # Deterministic based on location
    return random.uniform(0, 100)


def _get_risk_level_string(risk_score: float) -> str:
    """Convert risk score to level string."""
    if risk_score >= 80:
        return "critical"
    elif risk_score >= 60:
        return "high"
    elif risk_score >= 30:
        return "medium"
    else:
        return "low"
