from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from src.api.models import Advisory, RiskLevel

logger = logging.getLogger(__name__)


class AdvisoryGenerator:
    """Generates natural language advisories from risk data."""
    
    def __init__(self):
        self.active_advisories: Dict[str, Advisory] = {}
        
    async def get_active_advisories(self, 
                                  region_filter: Optional[str] = None,
                                  severity_filter: Optional[RiskLevel] = None,
                                  limit: int = 10) -> List[Advisory]:
        """Get currently active advisories."""
        try:
            # In production, this would query from database
            # For now, generate mock advisories
            mock_advisories = self._generate_mock_advisories()
            
            # Apply filters
            filtered_advisories = mock_advisories
            
            if region_filter:
                filtered_advisories = [
                    adv for adv in filtered_advisories 
                    if region_filter.lower() in [area.lower() for area in adv.affected_areas]
                ]
            
            if severity_filter:
                filtered_advisories = [
                    adv for adv in filtered_advisories 
                    if adv.severity == severity_filter
                ]
            
            # Sort by severity and issued time
            severity_order = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
            filtered_advisories.sort(
                key=lambda x: (severity_order.get(x.severity, 0), x.issued_at),
                reverse=True
            )
            
            return filtered_advisories[:limit]
            
        except Exception as e:
            logger.error(f"Get active advisories error: {str(e)}")
            return []
    
    async def generate_advisory_from_risk(self, risk_data: Dict[str, Any]) -> Advisory:
        """Generate advisory from risk assessment data."""
        try:
            risk_score = risk_data.get('risk_score', 0)
            location = risk_data.get('location', {})
            weather_conditions = risk_data.get('weather_conditions', {})
            
            # Determine severity
            severity = self._determine_severity(risk_score)
            
            # Generate title and message
            title, message = self._generate_advisory_content(risk_score, location, weather_conditions)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_score, weather_conditions)
            
            # Create advisory
            advisory = Advisory(
                id=str(uuid.uuid4()),
                title=title,
                message=message,
                severity=severity,
                affected_areas=[location.get('name', 'Unknown Area')],
                recommendations=recommendations,
                valid_until=datetime.utcnow() + timedelta(hours=6)
            )
            
            # Store in active advisories
            self.active_advisories[advisory.id] = advisory
            
            return advisory
            
        except Exception as e:
            logger.error(f"Advisory generation error: {str(e)}")
            # Return default advisory
            return Advisory(
                id=str(uuid.uuid4()),
                title="System Alert",
                message="Unable to generate advisory at this time",
                severity=RiskLevel.LOW,
                affected_areas=["System"],
                recommendations=["Monitor system status"],
                valid_until=datetime.utcnow() + timedelta(hours=1)
            )
    
    async def get_advisory_by_id(self, advisory_id: str) -> Optional[Advisory]:
        """Get advisory by ID."""
        return self.active_advisories.get(advisory_id)
    
    async def get_public_advisories(self, location: Optional[str] = None) -> List[Advisory]:
        """Get simplified advisories for public consumption."""
        try:
            all_advisories = await self.get_active_advisories()
            
            # Filter for public (high and critical severity only)
            public_advisories = [
                adv for adv in all_advisories 
                if adv.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            ]
            
            if location:
                public_advisories = [
                    adv for adv in public_advisories
                    if any(location.lower() in area.lower() for area in adv.affected_areas)
                ]
            
            return public_advisories
            
        except Exception as e:
            logger.error(f"Public advisories error: {str(e)}")
            return []
    
    async def get_historical_advisories(self,
                                      start_date: datetime,
                                      end_date: datetime,
                                      region: Optional[str] = None,
                                      limit: int = 50) -> List[Advisory]:
        """Get historical advisories for analysis."""
        try:
            # In production, this would query historical data from database
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Historical advisories error: {str(e)}")
            return []
    
    def _generate_mock_advisories(self) -> List[Advisory]:
        """Generate mock advisories for demonstration."""
        now = datetime.utcnow()
        
        advisories = [
            Advisory(
                id="ADV001",
                title="High Power Outage Risk - Bengaluru Urban",
                message="Severe weather conditions including heavy rainfall (45mm) and strong winds (65 km/h) are expected to significantly increase power outage risk in Bengaluru Urban district. Lightning activity and grid stress factors contribute to an elevated risk score of 72%.",
                severity=RiskLevel.HIGH,
                affected_areas=["Bengaluru Urban", "Bengaluru Rural"],
                issued_at=now - timedelta(minutes=30),
                valid_until=now + timedelta(hours=6),
                recommendations=[
                    "Ensure backup power systems are operational",
                    "Avoid outdoor activities during peak storm hours",
                    "Keep emergency supplies readily available",
                    "Monitor official weather updates"
                ]
            ),
            Advisory(
                id="ADV002", 
                title="Critical Storm Warning - Mumbai Suburban",
                message="CRITICAL: Extreme weather conditions with rainfall exceeding 75mm and wind speeds up to 85 km/h pose immediate threat to power infrastructure. Outage risk assessed at 89% with potential for widespread disruptions.",
                severity=RiskLevel.CRITICAL,
                affected_areas=["Mumbai Suburban", "Mumbai City", "Thane"],
                issued_at=now - timedelta(minutes=15),
                valid_until=now + timedelta(hours=4),
                recommendations=[
                    "Immediately activate emergency response protocols",
                    "Prioritize safety - avoid all non-essential travel",
                    "Ensure critical facilities have backup power",
                    "Stay indoors and away from windows",
                    "Monitor emergency broadcasts"
                ]
            ),
            Advisory(
                id="ADV003",
                title="Moderate Risk Alert - Chennai",
                message="Moderate weather conditions with intermittent rainfall (15mm) and moderate winds (35 km/h) may cause localized power disruptions. Grid stability remains good with 48% outage risk.",
                severity=RiskLevel.MEDIUM,
                affected_areas=["Chennai", "Kanchipuram"],
                issued_at=now - timedelta(hours=1),
                valid_until=now + timedelta(hours=8),
                recommendations=[
                    "Check backup power equipment",
                    "Secure outdoor equipment",
                    "Monitor local weather conditions"
                ]
            ),
            Advisory(
                id="ADV004",
                title="Grid Maintenance Notice - Delhi",
                message="Scheduled maintenance activities combined with increased electrical demand during peak hours may result in temporary power interruptions. Low outage risk of 25% expected.",
                severity=RiskLevel.LOW,
                affected_areas=["New Delhi", "South Delhi"],
                issued_at=now - timedelta(hours=2),
                valid_until=now + timedelta(hours=12),
                recommendations=[
                    "Plan activities around potential brief interruptions",
                    "No immediate action required"
                ]
            )
        ]
        
        return advisories
    
    def _determine_severity(self, risk_score: float) -> RiskLevel:
        """Determine advisory severity from risk score."""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_advisory_content(self, 
                                 risk_score: float, 
                                 location: Dict[str, Any],
                                 weather: Dict[str, Any]) -> tuple[str, str]:
        """Generate advisory title and message."""
        location_name = location.get('name', 'Affected Area')
        
        # Weather conditions
        rainfall = weather.get('rainfall', 0)
        wind_speed = weather.get('wind_speed', 0)
        lightning = weather.get('lightning_strikes', 0)
        storm_alert = weather.get('storm_alert', False)
        
        # Generate title
        if risk_score >= 80:
            title = f"CRITICAL: Power Outage Emergency - {location_name}"
        elif risk_score >= 60:
            title = f"HIGH RISK: Power Outage Warning - {location_name}"
        elif risk_score >= 30:
            title = f"MODERATE: Power Disruption Alert - {location_name}"
        else:
            title = f"LOW RISK: Routine Advisory - {location_name}"
        
        # Generate message
        weather_desc = []
        if rainfall > 50:
            weather_desc.append(f"extreme rainfall ({rainfall}mm)")
        elif rainfall > 25:
            weather_desc.append(f"heavy rainfall ({rainfall}mm)")
        elif rainfall > 0:
            weather_desc.append(f"rainfall ({rainfall}mm)")
        
        if wind_speed > 75:
            weather_desc.append(f"severe winds ({wind_speed} km/h)")
        elif wind_speed > 50:
            weather_desc.append(f"strong winds ({wind_speed} km/h)")
        elif wind_speed > 25:
            weather_desc.append(f"moderate winds ({wind_speed} km/h)")
        
        if lightning > 10:
            weather_desc.append("intense lightning activity")
        elif lightning > 5:
            weather_desc.append("significant lightning activity")
        elif lightning > 0:
            weather_desc.append("lightning activity")
        
        if storm_alert:
            weather_desc.append("active storm warning")
        
        weather_text = ", ".join(weather_desc) if weather_desc else "current weather conditions"
        
        if risk_score >= 80:
            urgency = "pose immediate threat"
        elif risk_score >= 60:
            urgency = "significantly increase"
        elif risk_score >= 30:
            urgency = "may cause"
        else:
            urgency = "present minimal risk for"
        
        message = (
            f"Weather conditions including {weather_text} {urgency} power outage risk "
            f"in {location_name}. Current assessment indicates {risk_score:.0f}% outage probability."
        )
        
        return title, message
    
    def _generate_recommendations(self, 
                                risk_score: float, 
                                weather: Dict[str, Any]) -> List[str]:
        """Generate safety and preparedness recommendations."""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_score >= 80:
            recommendations.extend([
                "Immediately activate emergency response protocols",
                "Ensure critical facilities have backup power operational",
                "Avoid all non-essential outdoor activities",
                "Monitor emergency broadcasts continuously"
            ])
        elif risk_score >= 60:
            recommendations.extend([
                "Ensure backup power systems are operational",
                "Secure outdoor equipment and loose objects",
                "Keep emergency supplies readily available",
                "Monitor official weather updates"
            ])
        elif risk_score >= 30:
            recommendations.extend([
                "Check backup power equipment functionality",
                "Prepare emergency supplies",
                "Monitor local weather conditions"
            ])
        else:
            recommendations.extend([
                "No immediate action required",
                "Continue normal activities with weather awareness"
            ])
        
        # Weather-specific recommendations
        rainfall = weather.get('rainfall', 0)
        wind_speed = weather.get('wind_speed', 0)
        lightning = weather.get('lightning_strikes', 0)
        
        if rainfall > 25:
            recommendations.extend([
                "Avoid flood-prone areas",
                "Do not attempt to drive through flooded roads"
            ])
        
        if wind_speed > 50:
            recommendations.extend([
                "Secure or bring indoors all loose outdoor items",
                "Avoid areas with large trees or weak structures"
            ])
        
        if lightning > 5:
            recommendations.extend([
                "Stay indoors and away from windows",
                "Unplug non-essential electronic devices",
                "Avoid using landline phones"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:8]  # Limit to 8 recommendations
