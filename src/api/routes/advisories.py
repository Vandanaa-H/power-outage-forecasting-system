from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from src.api.models import AdvisoryResponse, Advisory, RiskLevel
from src.utils.advisory_generator import AdvisoryGenerator
from src.utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize advisory generator
advisory_generator = AdvisoryGenerator()


async def get_advisory_generator():
    """Dependency to get the advisory generator."""
    return advisory_generator


@router.get("/advisories", response_model=AdvisoryResponse)
async def get_active_advisories(
    region: Optional[str] = Query(None, description="Filter by region"),
    severity: Optional[RiskLevel] = Query(None, description="Filter by severity level"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of advisories"),
    generator: AdvisoryGenerator = Depends(get_advisory_generator)
):
    """
    Get active weather and outage advisories.
    
    Returns current advisories with natural language descriptions.
    """
    try:
        # Generate cache key
        cache_key = f"advisories:{region}:{severity}:{limit}"
        
        # Check cache first
        cached_result = await get_cache(cache_key)
        if cached_result:
            logger.info("Returning cached advisories")
            return AdvisoryResponse(**cached_result)
        
        # Get active advisories
        advisories = await generator.get_active_advisories(
            region_filter=region,
            severity_filter=severity,
            limit=limit
        )
        
        # Create response
        response = AdvisoryResponse(
            advisories=advisories,
            total_count=len(advisories),
            active_count=len([a for a in advisories if a.valid_until > datetime.utcnow()])
        )
        
        # Cache for 2 minutes
        await set_cache(cache_key, response.dict(), ttl=120)
        
        logger.info(f"Retrieved {len(advisories)} advisories")
        return response
        
    except Exception as e:
        logger.error(f"Advisories retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get advisories: {str(e)}")


@router.post("/advisories/generate")
async def generate_advisory(
    risk_data: Dict[str, Any],
    generator: AdvisoryGenerator = Depends(get_advisory_generator)
):
    """
    Generate a new advisory based on current risk conditions.
    
    Creates natural language advisories from risk assessment data.
    """
    try:
        # Validate input
        required_fields = ['risk_score', 'location', 'weather_conditions']
        for field in required_fields:
            if field not in risk_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Generate advisory
        advisory = await generator.generate_advisory_from_risk(risk_data)
        
        logger.info(f"Generated advisory: {advisory.id}")
        return advisory
        
    except Exception as e:
        logger.error(f"Advisory generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Advisory generation failed: {str(e)}")


@router.get("/advisories/{advisory_id}")
async def get_advisory_details(
    advisory_id: str,
    generator: AdvisoryGenerator = Depends(get_advisory_generator)
):
    """
    Get detailed information about a specific advisory.
    
    Returns full advisory details including recommendations and updates.
    """
    try:
        advisory = await generator.get_advisory_by_id(advisory_id)
        
        if not advisory:
            raise HTTPException(status_code=404, detail="Advisory not found")
        
        return advisory
        
    except Exception as e:
        logger.error(f"Advisory details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get advisory details: {str(e)}")


@router.get("/advisories/public/summary")
async def get_public_advisory_summary(
    location: Optional[str] = Query(None, description="Location filter"),
    generator: AdvisoryGenerator = Depends(get_advisory_generator)
):
    """
    Get simplified advisory summary for public consumption.
    
    Returns citizen-friendly advisory information.
    """
    try:
        # Get public advisories
        public_advisories = await generator.get_public_advisories(location)
        
        # Create simplified summary
        summary = {
            "current_alert_level": "normal",  # Would be determined from active advisories
            "key_messages": [],
            "affected_areas": [],
            "recommendations": [],
            "last_updated": datetime.utcnow(),
            "next_update": datetime.utcnow() + timedelta(hours=1)
        }
        
        if public_advisories:
            # Determine overall alert level
            max_severity = max(adv.severity for adv in public_advisories)
            summary["current_alert_level"] = max_severity.value
            
            # Compile key messages
            summary["key_messages"] = [adv.message for adv in public_advisories[:3]]
            
            # Get affected areas
            affected_areas = set()
            for adv in public_advisories:
                affected_areas.update(adv.affected_areas)
            summary["affected_areas"] = list(affected_areas)
            
            # Compile recommendations
            recommendations = set()
            for adv in public_advisories:
                recommendations.update(adv.recommendations)
            summary["recommendations"] = list(recommendations)[:5]  # Top 5
        
        return summary
        
    except Exception as e:
        logger.error(f"Public advisory summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get public summary: {str(e)}")


@router.post("/advisories/subscribe")
async def subscribe_to_advisories(
    subscription_data: Dict[str, Any]
):
    """
    Subscribe to advisory notifications.
    
    Allows users to subscribe to SMS/email alerts for specific regions or risk levels.
    """
    try:
        # Validate subscription data
        required_fields = ['contact_method', 'contact_value', 'preferences']
        for field in required_fields:
            if field not in subscription_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create subscription
        subscription_id = str(uuid.uuid4())
        
        # In production, this would save to database
        subscription = {
            "id": subscription_id,
            "contact_method": subscription_data["contact_method"],
            "contact_value": subscription_data["contact_value"],
            "preferences": subscription_data["preferences"],
            "created_at": datetime.utcnow(),
            "active": True
        }
        
        logger.info(f"Created advisory subscription: {subscription_id}")
        return {
            "subscription_id": subscription_id,
            "status": "active",
            "message": "Successfully subscribed to advisory notifications"
        }
        
    except Exception as e:
        logger.error(f"Advisory subscription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")


@router.get("/advisories/history")
async def get_advisory_history(
    start_date: datetime = Query(..., description="Start date for history"),
    end_date: datetime = Query(..., description="End date for history"),
    region: Optional[str] = Query(None, description="Region filter"),
    limit: int = Query(50, ge=1, le=200),
    generator: AdvisoryGenerator = Depends(get_advisory_generator)
):
    """
    Get historical advisories for analysis and reporting.
    
    Useful for post-event analysis and model performance evaluation.
    """
    try:
        # Validate date range
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if (end_date - start_date).days > 90:
            raise HTTPException(status_code=400, detail="Date range limited to 90 days")
        
        # Get historical advisories
        historical_advisories = await generator.get_historical_advisories(
            start_date=start_date,
            end_date=end_date,
            region=region,
            limit=limit
        )
        
        # Calculate statistics
        statistics = {
            "total_advisories": len(historical_advisories),
            "by_severity": {},
            "by_region": {},
            "average_duration": 0,
            "most_common_causes": []
        }
        
        # Calculate severity distribution
        for adv in historical_advisories:
            severity = adv.severity.value
            statistics["by_severity"][severity] = statistics["by_severity"].get(severity, 0) + 1
        
        return {
            "advisories": historical_advisories,
            "statistics": statistics,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
        
    except Exception as e:
        logger.error(f"Advisory history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get advisory history: {str(e)}")
