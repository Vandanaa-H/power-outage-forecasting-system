import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
from datetime import datetime
import json

from src.api.models import BoundingBox, HeatmapPoint

logger = logging.getLogger(__name__)


class GeoSpatialProcessor:
    """Geospatial data processing and analysis utilities."""
    
    def __init__(self):
        self.region_data = {}
        self.grid_points = {}
        
    async def generate_grid_points(self, 
                                 bbox: BoundingBox, 
                                 resolution: int = 50) -> List[Dict[str, Any]]:
        """Generate grid points within bounding box for heatmap."""
        try:
            # Calculate step size
            lat_step = (bbox.north - bbox.south) / resolution
            lon_step = (bbox.east - bbox.west) / resolution
            
            grid_points = []
            
            for i in range(resolution):
                for j in range(resolution):
                    lat = bbox.south + i * lat_step
                    lon = bbox.west + j * lon_step
                    
                    # Get region information for this point
                    region_info = await self._get_region_info(lat, lon)
                    
                    point = {
                        'latitude': lat,
                        'longitude': lon,
                        'region_name': region_info.get('name', 'Unknown'),
                        'population': region_info.get('population'),
                        'grid_id': f"{i}_{j}"
                    }
                    
                    grid_points.append(point)
            
            logger.info(f"Generated {len(grid_points)} grid points")
            return grid_points
            
        except Exception as e:
            logger.error(f"Grid point generation error: {str(e)}")
            return []
    
    async def get_regional_risk_summary(self, region_type: str = "district") -> List[Dict[str, Any]]:
        """Get risk summary aggregated by administrative regions."""
        try:
            # Mock regional data for demonstration
            # In production, this would query actual administrative boundaries
            if region_type == "district":
                regions = [
                    {"name": "Bengaluru Urban", "risk_score": 72.5, "population": 9621551, "lat": 12.9716, "lon": 77.5946},
                    {"name": "Mumbai Suburban", "risk_score": 65.3, "population": 9356962, "lat": 19.0760, "lon": 72.8777},
                    {"name": "Delhi", "risk_score": 58.7, "population": 16787941, "lat": 28.7041, "lon": 77.1025},
                    {"name": "Chennai", "risk_score": 45.2, "population": 4681087, "lat": 13.0827, "lon": 80.2707},
                    {"name": "Kolkata", "risk_score": 52.8, "population": 4496694, "lat": 22.5726, "lon": 88.3639},
                    {"name": "Hyderabad", "risk_score": 38.9, "population": 6809970, "lat": 17.3850, "lon": 78.4867},
                    {"name": "Pune", "risk_score": 42.1, "population": 3124458, "lat": 18.5204, "lon": 73.8567},
                    {"name": "Ahmedabad", "risk_score": 35.6, "population": 5570585, "lat": 23.0225, "lon": 72.5714}
                ]
            elif region_type == "state":
                regions = [
                    {"name": "Maharashtra", "risk_score": 55.4, "population": 112372972, "lat": 19.7515, "lon": 75.7139},
                    {"name": "Karnataka", "risk_score": 68.2, "population": 61130704, "lat": 15.3173, "lon": 75.7139},
                    {"name": "Tamil Nadu", "risk_score": 44.7, "population": 72138958, "lat": 11.1271, "lon": 78.6569},
                    {"name": "West Bengal", "risk_score": 51.9, "population": 91347736, "lat": 22.9868, "lon": 87.8550},
                    {"name": "Gujarat", "risk_score": 37.3, "population": 60383628, "lat": 22.2587, "lon": 71.1924}
                ]
            else:
                regions = []
            
            # Add timestamp and additional metadata
            for region in regions:
                region.update({
                    "timestamp": datetime.utcnow(),
                    "risk_level": self._get_risk_level_from_score(region["risk_score"]),
                    "estimated_affected": int(region["population"] * region["risk_score"] / 10000)  # Rough estimate
                })
            
            return regions
            
        except Exception as e:
            logger.error(f"Regional risk summary error: {str(e)}")
            return []
    
    async def get_live_risk_updates(self) -> List[Dict[str, Any]]:
        """Get live risk updates for real-time monitoring."""
        try:
            # Mock live updates
            updates = [
                {
                    "location": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru"},
                    "risk_score": 75.2,
                    "change": +5.3,
                    "timestamp": datetime.utcnow(),
                    "reason": "Increased lightning activity",
                    "severity": "high"
                },
                {
                    "location": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
                    "risk_score": 68.7,
                    "change": +2.1,
                    "timestamp": datetime.utcnow(),
                    "reason": "Heavy rainfall warning issued",
                    "severity": "high"
                },
                {
                    "location": {"lat": 13.0827, "lon": 80.2707, "name": "Chennai"},
                    "risk_score": 42.8,
                    "change": -3.4,
                    "timestamp": datetime.utcnow(),
                    "reason": "Storm alert lifted",
                    "severity": "medium"
                }
            ]
            
            return updates
            
        except Exception as e:
            logger.error(f"Live risk updates error: {str(e)}")
            return []
    
    async def calculate_distance_matrix(self, 
                                      points: List[Tuple[float, float]]) -> np.ndarray:
        """Calculate distance matrix between geographic points."""
        try:
            n_points = len(points)
            distance_matrix = np.zeros((n_points, n_points))
            
            for i in range(n_points):
                for j in range(i+1, n_points):
                    distance = self._haversine_distance(
                        points[i][0], points[i][1],
                        points[j][0], points[j][1]
                    )
                    distance_matrix[i][j] = distance
                    distance_matrix[j][i] = distance
            
            return distance_matrix
            
        except Exception as e:
            logger.error(f"Distance matrix calculation error: {str(e)}")
            return np.array([])
    
    async def find_nearby_substations(self, 
                                    latitude: float, 
                                    longitude: float,
                                    radius_km: float = 50) -> List[Dict[str, Any]]:
        """Find substations within specified radius."""
        try:
            # Mock substation data
            substations = [
                {"id": "SUB001", "name": "Yeshwantpur", "lat": 13.0280, "lon": 77.5407, "capacity_mw": 220},
                {"id": "SUB002", "name": "Lingarajapuram", "lat": 13.0067, "lon": 77.6413, "capacity_mw": 110},
                {"id": "SUB003", "name": "Mysore Road", "lat": 12.9395, "lon": 77.5462, "capacity_mw": 66},
                {"id": "SUB004", "name": "Electronic City", "lat": 12.8456, "lon": 77.6603, "capacity_mw": 110},
                {"id": "SUB005", "name": "Whitefield", "lat": 12.9698, "lon": 77.7500, "capacity_mw": 66}
            ]
            
            nearby = []
            for station in substations:
                distance = self._haversine_distance(
                    latitude, longitude,
                    station["lat"], station["lon"]
                )
                
                if distance <= radius_km:
                    station["distance_km"] = round(distance, 2)
                    nearby.append(station)
            
            # Sort by distance
            nearby.sort(key=lambda x: x["distance_km"])
            
            return nearby
            
        except Exception as e:
            logger.error(f"Nearby substations search error: {str(e)}")
            return []
    
    async def analyze_spatial_correlation(self, 
                                        risk_data: List[HeatmapPoint]) -> Dict[str, Any]:
        """Analyze spatial correlation patterns in risk data."""
        try:
            if len(risk_data) < 3:
                return {"correlation": "insufficient_data"}
            
            # Extract coordinates and risk scores
            coordinates = [(point.latitude, point.longitude) for point in risk_data]
            risk_scores = [point.risk_score for point in risk_data]
            
            # Calculate distance matrix
            distance_matrix = await self.calculate_distance_matrix(coordinates)
            
            # Calculate spatial autocorrelation (simplified Moran's I)
            spatial_correlation = self._calculate_morans_i(risk_scores, distance_matrix)
            
            # Identify clusters
            clusters = self._identify_risk_clusters(risk_data)
            
            analysis = {
                "spatial_autocorrelation": spatial_correlation,
                "clustering_detected": len(clusters) > 0,
                "risk_clusters": clusters,
                "hotspots": [point for point in risk_data if point.risk_score > 70],
                "coldspots": [point for point in risk_data if point.risk_score < 30]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Spatial correlation analysis error: {str(e)}")
            return {"correlation": "analysis_failed"}
    
    async def _get_region_info(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get region information for a geographic point."""
        try:
            # Mock region lookup based on coordinates
            # In production, this would use actual GIS data
            
            # Karnataka regions
            if 11.5 <= latitude <= 18.5 and 74.0 <= longitude <= 78.5:
                if 12.8 <= latitude <= 13.2 and 77.3 <= longitude <= 77.8:
                    return {"name": "Bengaluru Urban", "state": "Karnataka", "population": 100000}
                else:
                    return {"name": "Karnataka Rural", "state": "Karnataka", "population": 50000}
            
            # Maharashtra regions
            elif 15.5 <= latitude <= 22.0 and 72.5 <= longitude <= 80.5:
                if 18.8 <= latitude <= 19.3 and 72.7 <= longitude <= 73.0:
                    return {"name": "Mumbai Suburban", "state": "Maharashtra", "population": 150000}
                else:
                    return {"name": "Maharashtra Rural", "state": "Maharashtra", "population": 75000}
            
            # Tamil Nadu regions
            elif 8.0 <= latitude <= 13.5 and 76.0 <= longitude <= 80.5:
                if 12.9 <= latitude <= 13.2 and 80.1 <= longitude <= 80.3:
                    return {"name": "Chennai", "state": "Tamil Nadu", "population": 120000}
                else:
                    return {"name": "Tamil Nadu Rural", "state": "Tamil Nadu", "population": 60000}
            
            else:
                return {"name": "Unknown Region", "state": "Unknown", "population": 25000}
                
        except Exception as e:
            logger.error(f"Region info lookup error: {str(e)}")
            return {"name": "Error Region", "state": "Unknown", "population": 0}
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _calculate_morans_i(self, values: List[float], distance_matrix: np.ndarray) -> float:
        """Calculate Moran's I spatial autocorrelation statistic."""
        try:
            n = len(values)
            if n < 2:
                return 0.0
            
            # Create weights matrix (inverse distance)
            weights = np.zeros_like(distance_matrix)
            for i in range(n):
                for j in range(n):
                    if i != j and distance_matrix[i][j] > 0:
                        weights[i][j] = 1.0 / distance_matrix[i][j]
            
            # Normalize weights
            row_sums = weights.sum(axis=1)
            for i in range(n):
                if row_sums[i] > 0:
                    weights[i] = weights[i] / row_sums[i]
            
            # Calculate Moran's I
            mean_value = np.mean(values)
            numerator = 0
            denominator = 0
            
            for i in range(n):
                for j in range(n):
                    numerator += weights[i][j] * (values[i] - mean_value) * (values[j] - mean_value)
                denominator += (values[i] - mean_value) ** 2
            
            if denominator == 0:
                return 0.0
            
            morans_i = (n / np.sum(weights)) * (numerator / denominator)
            return float(morans_i)
            
        except Exception as e:
            logger.error(f"Moran's I calculation error: {str(e)}")
            return 0.0
    
    def _identify_risk_clusters(self, risk_data: List[HeatmapPoint]) -> List[Dict[str, Any]]:
        """Identify clusters of high-risk areas."""
        try:
            high_risk_points = [point for point in risk_data if point.risk_score > 60]
            
            if len(high_risk_points) < 2:
                return []
            
            clusters = []
            processed = set()
            
            for i, point in enumerate(high_risk_points):
                if i in processed:
                    continue
                
                cluster = [point]
                cluster_indices = {i}
                
                # Find nearby high-risk points
                for j, other_point in enumerate(high_risk_points):
                    if j in processed or j == i:
                        continue
                    
                    distance = self._haversine_distance(
                        point.latitude, point.longitude,
                        other_point.latitude, other_point.longitude
                    )
                    
                    if distance < 50:  # Within 50km
                        cluster.append(other_point)
                        cluster_indices.add(j)
                
                if len(cluster) > 1:
                    # Calculate cluster center
                    center_lat = np.mean([p.latitude for p in cluster])
                    center_lon = np.mean([p.longitude for p in cluster])
                    avg_risk = np.mean([p.risk_score for p in cluster])
                    
                    clusters.append({
                        "center": {"latitude": center_lat, "longitude": center_lon},
                        "average_risk": avg_risk,
                        "point_count": len(cluster),
                        "affected_regions": list(set([p.region_name for p in cluster]))
                    })
                    
                    processed.update(cluster_indices)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Risk cluster identification error: {str(e)}")
            return []
    
    def _get_risk_level_from_score(self, risk_score: float) -> str:
        """Convert risk score to level string."""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"
