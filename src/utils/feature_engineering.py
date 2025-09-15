import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from sklearn.preprocessing import StandardScaler
import calendar

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering utilities for outage prediction."""
    
    def __init__(self):
        self.scalers = {}
        
    def extract_temporal_features(self, timestamp: datetime) -> Dict[str, float]:
        """Extract temporal features from timestamp."""
        try:
            features = {
                'hour_of_day': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'day_of_month': timestamp.day,
                'month': timestamp.month,
                'quarter': (timestamp.month - 1) // 3 + 1,
                'season': self._get_season(timestamp.month),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'is_peak_hour': 1 if timestamp.hour in [8, 9, 10, 17, 18, 19, 20] else 0,
                'is_night': 1 if timestamp.hour < 6 or timestamp.hour > 22 else 0
            }
            
            # Cyclical encoding for periodic features
            features.update({
                'hour_sin': np.sin(2 * np.pi * timestamp.hour / 24),
                'hour_cos': np.cos(2 * np.pi * timestamp.hour / 24),
                'day_sin': np.sin(2 * np.pi * timestamp.weekday() / 7),
                'day_cos': np.cos(2 * np.pi * timestamp.weekday() / 7),
                'month_sin': np.sin(2 * np.pi * timestamp.month / 12),
                'month_cos': np.cos(2 * np.pi * timestamp.month / 12)
            })
            
            return features
            
        except Exception as e:
            logger.error(f"Temporal feature extraction error: {str(e)}")
            return {}
    
    def engineer_weather_features(self, weather_data: Dict[str, Any]) -> Dict[str, float]:
        """Engineer advanced weather features."""
        try:
            features = weather_data.copy()
            
            # Temperature-based features
            temp = weather_data.get('temperature', 25)
            features['temp_extreme'] = 1 if temp > 40 or temp < 5 else 0
            features['temp_squared'] = temp ** 2
            features['heat_index'] = self._calculate_heat_index(temp, weather_data.get('humidity', 60))
            
            # Wind-based features
            wind_speed = weather_data.get('wind_speed', 0)
            features['wind_category'] = self._categorize_wind_speed(wind_speed)
            features['wind_squared'] = wind_speed ** 2
            
            # Rainfall features
            rainfall = weather_data.get('rainfall', 0)
            features['rainfall_category'] = self._categorize_rainfall(rainfall)
            features['heavy_rain'] = 1 if rainfall > 25 else 0
            features['extreme_rain'] = 1 if rainfall > 50 else 0
            
            # Lightning features
            lightning = weather_data.get('lightning_strikes', 0)
            features['lightning_risk'] = min(lightning / 10, 1.0)  # Normalize to 0-1
            features['high_lightning'] = 1 if lightning > 5 else 0
            
            # Combined risk features
            features['weather_severity_score'] = self._calculate_weather_severity(features)
            features['storm_intensity'] = (
                features['wind_squared'] * 0.3 + 
                features['rainfall'] * 0.4 + 
                features['lightning_risk'] * 0.3
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Weather feature engineering error: {str(e)}")
            return weather_data
    
    def engineer_grid_features(self, grid_data: Dict[str, Any]) -> Dict[str, float]:
        """Engineer advanced grid features."""
        try:
            features = grid_data.copy()
            
            # Load-based features
            load_factor = grid_data.get('load_factor', 0.5)
            features['load_stress'] = max(0, load_factor - 0.8)  # Stress above 80%
            features['load_squared'] = load_factor ** 2
            features['high_load'] = 1 if load_factor > 0.85 else 0
            
            # Voltage stability features
            voltage_stability = grid_data.get('voltage_stability', 1.0)
            features['voltage_risk'] = 1 - voltage_stability
            features['low_voltage'] = 1 if voltage_stability < 0.7 else 0
            features['critical_voltage'] = 1 if voltage_stability < 0.5 else 0
            
            # Historical outages
            historical_outages = grid_data.get('historical_outages', 0)
            features['outage_frequency'] = min(historical_outages / 10, 1.0)  # Normalize
            features['high_outage_history'] = 1 if historical_outages > 5 else 0
            
            # Equipment health
            feeder_health = grid_data.get('feeder_health', 1.0)
            features['equipment_risk'] = 1 - feeder_health
            features['poor_equipment'] = 1 if feeder_health < 0.6 else 0
            
            # Combined grid risk
            features['grid_vulnerability_score'] = (
                features['load_stress'] * 0.3 +
                features['voltage_risk'] * 0.3 +
                features['equipment_risk'] * 0.2 +
                features['outage_frequency'] * 0.2
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Grid feature engineering error: {str(e)}")
            return grid_data
    
    def create_lag_features(self, 
                           time_series_data: pd.DataFrame, 
                           target_column: str,
                           lag_periods: List[int] = [1, 3, 6, 12, 24]) -> pd.DataFrame:
        """Create lag features for time series data."""
        try:
            df = time_series_data.copy()
            
            for lag in lag_periods:
                df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
            
            # Rolling statistics
            for window in [3, 6, 12, 24]:
                df[f'{target_column}_rolling_mean_{window}'] = df[target_column].rolling(window).mean()
                df[f'{target_column}_rolling_std_{window}'] = df[target_column].rolling(window).std()
                df[f'{target_column}_rolling_max_{window}'] = df[target_column].rolling(window).max()
                df[f'{target_column}_rolling_min_{window}'] = df[target_column].rolling(window).min()
            
            # Exponential weighted features
            df[f'{target_column}_ewm_3'] = df[target_column].ewm(span=3).mean()
            df[f'{target_column}_ewm_12'] = df[target_column].ewm(span=12).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Lag feature creation error: {str(e)}")
            return time_series_data
    
    def create_interaction_features(self, 
                                   weather_features: Dict[str, float],
                                   grid_features: Dict[str, float]) -> Dict[str, float]:
        """Create interaction features between weather and grid data."""
        try:
            interactions = {}
            
            # Weather-grid interactions
            rainfall = weather_features.get('rainfall', 0)
            wind_speed = weather_features.get('wind_speed', 0)
            load_factor = grid_features.get('load_factor', 0.5)
            voltage_stability = grid_features.get('voltage_stability', 1.0)
            
            # Critical combinations
            interactions['rain_wind_interaction'] = rainfall * wind_speed
            interactions['weather_load_stress'] = (rainfall + wind_speed) * load_factor
            interactions['storm_voltage_risk'] = (rainfall + wind_speed) * (1 - voltage_stability)
            interactions['lightning_equipment_risk'] = (
                weather_features.get('lightning_strikes', 0) * 
                (1 - grid_features.get('feeder_health', 1.0))
            )
            
            # High-risk combinations
            interactions['extreme_weather_high_load'] = (
                (1 if rainfall > 25 or wind_speed > 50 else 0) * 
                (1 if load_factor > 0.8 else 0)
            )
            
            interactions['storm_maintenance_risk'] = (
                (1 if weather_features.get('storm_alert', False) else 0) *
                (1 if grid_features.get('maintenance_status', False) else 0)
            )
            
            return interactions
            
        except Exception as e:
            logger.error(f"Interaction feature creation error: {str(e)}")
            return {}
    
    def _get_season(self, month: int) -> int:
        """Get season from month (for India: 0=Winter, 1=Summer, 2=Monsoon)."""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Summer
        elif month in [6, 7, 8, 9]:
            return 2  # Monsoon
        else:
            return 3  # Post-monsoon
    
    def _calculate_heat_index(self, temperature: float, humidity: float) -> float:
        """Calculate heat index from temperature and humidity."""
        if temperature < 27:  # Heat index not applicable
            return temperature
        
        # Simplified heat index calculation
        hi = (
            -8.78469475556 +
            1.61139411 * temperature +
            2.33854883889 * humidity +
            -0.14611605 * temperature * humidity +
            -0.012308094 * temperature ** 2 +
            -0.0164248277778 * humidity ** 2 +
            0.002211732 * temperature ** 2 * humidity +
            0.00072546 * temperature * humidity ** 2 +
            -0.000003582 * temperature ** 2 * humidity ** 2
        )
        
        return max(temperature, hi)
    
    def _categorize_wind_speed(self, wind_speed: float) -> int:
        """Categorize wind speed (0=Calm, 1=Light, 2=Moderate, 3=Strong, 4=Severe)."""
        if wind_speed < 10:
            return 0
        elif wind_speed < 25:
            return 1
        elif wind_speed < 50:
            return 2
        elif wind_speed < 75:
            return 3
        else:
            return 4
    
    def _categorize_rainfall(self, rainfall: float) -> int:
        """Categorize rainfall intensity (0=No rain, 1=Light, 2=Moderate, 3=Heavy, 4=Extreme)."""
        if rainfall == 0:
            return 0
        elif rainfall < 2.5:
            return 1
        elif rainfall < 10:
            return 2
        elif rainfall < 50:
            return 3
        else:
            return 4
    
    def _calculate_weather_severity(self, features: Dict[str, float]) -> float:
        """Calculate overall weather severity score."""
        severity = 0.0
        
        # Temperature contribution
        if features.get('temp_extreme', 0):
            severity += 0.2
        
        # Wind contribution
        wind_cat = features.get('wind_category', 0)
        severity += wind_cat * 0.15
        
        # Rainfall contribution
        rain_cat = features.get('rainfall_category', 0)
        severity += rain_cat * 0.25
        
        # Lightning contribution
        if features.get('high_lightning', 0):
            severity += 0.2
        
        # Storm alert
        if features.get('storm_alert', False):
            severity += 0.2
        
        return min(severity, 1.0)
