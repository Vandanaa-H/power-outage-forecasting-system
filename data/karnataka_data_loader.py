"""
Karnataka-specific dataset downloader and processor.
This module handles real data for Karnataka power outage forecasting.
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KarnatakaDataLoader:
    """Load and process Karnataka-specific power and weather data."""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Karnataka districts and major cities
        self.karnataka_cities = {
            'bangalore_urban': {'lat': 12.9716, 'lon': 77.5946, 'priority': 1, 'population': 12300000},
            'bangalore_rural': {'lat': 13.0843, 'lon': 77.5847, 'priority': 1, 'population': 991000},
            'mysore': {'lat': 12.2958, 'lon': 76.6394, 'priority': 1, 'population': 3000000},
            'hubli_dharwad': {'lat': 15.3647, 'lon': 75.1240, 'priority': 1, 'population': 1800000},
            'mangalore': {'lat': 12.9141, 'lon': 74.8560, 'priority': 2, 'population': 623000},
            'belgaum': {'lat': 15.8497, 'lon': 74.4977, 'priority': 2, 'population': 610000},
            'gulbarga': {'lat': 17.3297, 'lon': 76.8343, 'priority': 2, 'population': 543000},
            'davangere': {'lat': 14.4644, 'lon': 75.9932, 'priority': 2, 'population': 434000},
            'bellary': {'lat': 15.1394, 'lon': 76.9214, 'priority': 2, 'population': 410000},
            'bijapur': {'lat': 16.8302, 'lon': 75.7100, 'priority': 2, 'population': 327000}
        }
        
        # ESCOM boundaries (Karnataka power distribution companies)
        self.escom_zones = {
            'BESCOM': ['bangalore_urban', 'bangalore_rural', 'chitradurga', 'kolar', 'tumkur'],
            'MESCOM': ['mangalore', 'udupi', 'hassan', 'chikmagalur', 'madikeri'],
            'HESCOM': ['hubli_dharwad', 'bellary', 'bagalkot', 'bijapur', 'gadag'],
            'GESCOM': ['gulbarga', 'bidar', 'raichur', 'koppal', 'yadgir'],
            'CHESCOM': ['mysore', 'chamarajanagar', 'mandya', 'hassan']
        }
    
    def generate_realistic_karnataka_data(self, years=5, samples_per_day=24):
        """Generate realistic power outage data for Karnataka."""
        logger.info(f"Generating {years} years of Karnataka power outage data")
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        all_data = []
        
        for city_name, city_info in self.karnataka_cities.items():
            logger.info(f"Generating data for {city_name}")
            
            # Generate hourly data for each city
            current_date = start_date
            while current_date <= end_date:
                hour_data = self._generate_city_hour_data(city_name, city_info, current_date)
                all_data.extend(hour_data)
                current_date += timedelta(days=1)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        output_file = self.data_dir / "karnataka_power_outage_dataset.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Saved Karnataka dataset to {output_file}")
        
        return df
    
    def _generate_city_hour_data(self, city_name, city_info, date):
        """Generate 24 hours of realistic data for a city."""
        lat, lon = city_info['lat'], city_info['lon']
        priority = city_info['priority']
        population = city_info['population']
        
        # Determine season and weather patterns
        month = date.month
        is_monsoon = month in [6, 7, 8, 9]  # June-September
        is_summer = month in [3, 4, 5]      # March-May
        is_winter = month in [12, 1, 2]     # Dec-Feb
        
        day_data = []
        
        for hour in range(24):
            timestamp = date.replace(hour=hour)
            
            # Weather generation based on Karnataka patterns
            weather_data = self._generate_karnataka_weather(lat, lon, timestamp, is_monsoon, is_summer)
            
            # Power grid data based on city characteristics
            grid_data = self._generate_grid_data(city_name, city_info, timestamp, weather_data)
            
            # Outage probability based on multiple factors
            outage_prob = self._calculate_outage_probability(weather_data, grid_data, city_info, timestamp)
            
            # Record
            record = {
                'timestamp': timestamp.isoformat(),
                'city': city_name,
                'latitude': lat,
                'longitude': lon,
                'escom_zone': self._get_escom_zone(city_name),
                'priority_tier': priority,
                'population': population,
                
                # Weather features
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'wind_speed': weather_data['wind_speed'],
                'rainfall': weather_data['rainfall'],
                'lightning_strikes': weather_data['lightning_strikes'],
                'storm_alert': weather_data['storm_alert'],
                'is_monsoon': is_monsoon,
                'is_summer': is_summer,
                
                # Grid features
                'load_factor': grid_data['load_factor'],
                'voltage_stability': grid_data['voltage_stability'],
                'historical_outages': grid_data['historical_outages'],
                'maintenance_status': grid_data['maintenance_status'],
                'feeder_health': grid_data['feeder_health'],
                'transformer_load': grid_data['transformer_load'],
                
                # Temporal features
                'hour_of_day': hour,
                'day_of_week': timestamp.weekday(),
                'month': month,
                'season': 0 if is_winter else 1 if is_summer else 2 if is_monsoon else 3,
                
                # Target variables
                'outage_probability': outage_prob,
                'outage_occurred': 1 if outage_prob > np.random.uniform(0.3, 0.8) else 0,
                'outage_duration_minutes': max(0, np.random.exponential(45) if outage_prob > 0.6 else 0),
                'affected_customers': int(population * outage_prob * np.random.uniform(0.1, 0.3))
            }
            
            day_data.append(record)
        
        return day_data
    
    def _generate_karnataka_weather(self, lat, lon, timestamp, is_monsoon, is_summer):
        """Generate realistic weather data for Karnataka location."""
        hour = timestamp.hour
        month = timestamp.month
        
        # Base temperature patterns for Karnataka
        if is_summer:
            base_temp = 32 + np.random.normal(0, 4)  # Hot summers
        elif is_monsoon:
            base_temp = 26 + np.random.normal(0, 3)  # Cooler during monsoon
        else:
            base_temp = 24 + np.random.normal(0, 3)  # Pleasant winter
        
        # Daily temperature variation
        temp_variation = np.sin((hour - 6) * np.pi / 12) * 6
        temperature = base_temp + temp_variation
        
        # Humidity patterns
        if is_monsoon:
            humidity = np.clip(75 + np.random.normal(0, 10), 60, 95)
        elif is_summer:
            humidity = np.clip(35 + np.random.normal(0, 15), 20, 70)
        else:
            humidity = np.clip(55 + np.random.normal(0, 10), 40, 80)
        
        # Wind patterns
        if lat > 15:  # North Karnataka (more windy)
            wind_speed = np.clip(np.random.exponential(12), 0, 80)
        else:  # South Karnataka
            wind_speed = np.clip(np.random.exponential(8), 0, 60)
        
        # Rainfall patterns (critical for Karnataka)
        if is_monsoon:
            # Heavy monsoon rains
            rainfall = max(0, np.random.exponential(15))
            if np.random.random() < 0.3:  # 30% chance of heavy rain
                rainfall += np.random.exponential(25)
        elif month in [10, 11]:  # Post-monsoon
            rainfall = max(0, np.random.exponential(3))
        else:
            rainfall = max(0, np.random.exponential(0.5))
        
        # Lightning (major cause of outages in Karnataka)
        if rainfall > 10:
            lightning_strikes = np.random.poisson(3)
        elif rainfall > 5:
            lightning_strikes = np.random.poisson(1)
        else:
            lightning_strikes = np.random.poisson(0.2)
        
        # Storm alerts
        storm_alert = 1 if (rainfall > 25 or wind_speed > 40 or lightning_strikes > 5) else 0
        
        return {
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'wind_speed': round(wind_speed, 1),
            'rainfall': round(rainfall, 1),
            'lightning_strikes': int(lightning_strikes),
            'storm_alert': storm_alert
        }
    
    def _generate_grid_data(self, city_name, city_info, timestamp, weather_data):
        """Generate realistic grid data based on Karnataka power system."""
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5
        priority = city_info['priority']
        
        # Load factor patterns
        if city_name in ['bangalore_urban', 'bangalore_rural']:
            # IT city patterns - high during day, moderate at night
            if 9 <= hour <= 18:  # Work hours
                base_load = 0.85 + np.random.normal(0, 0.1)
            elif 19 <= hour <= 23:  # Evening peak
                base_load = 0.9 + np.random.normal(0, 0.05)
            else:  # Night/early morning
                base_load = 0.6 + np.random.normal(0, 0.1)
        elif priority == 2:  # Industrial cities
            if 8 <= hour <= 20:  # Industrial hours
                base_load = 0.8 + np.random.normal(0, 0.1)
            else:
                base_load = 0.5 + np.random.normal(0, 0.1)
        else:  # Other areas
            if 18 <= hour <= 22:  # Evening peak
                base_load = 0.75 + np.random.normal(0, 0.1)
            else:
                base_load = 0.55 + np.random.normal(0, 0.1)
        
        # Weather impact on load
        if weather_data['temperature'] > 35:  # AC load
            base_load += 0.1
        if weather_data['rainfall'] > 10:  # Pumping load
            base_load += 0.05
        
        load_factor = np.clip(base_load, 0.2, 0.98)
        
        # Voltage stability (affected by load and weather)
        base_stability = 0.92 - (load_factor - 0.7) * 0.3
        if weather_data['storm_alert']:
            base_stability -= 0.15
        voltage_stability = np.clip(base_stability + np.random.normal(0, 0.05), 0.6, 0.99)
        
        # Historical outages (city-specific patterns)
        if priority == 1:  # Tier 1 cities - better infrastructure
            hist_outages = np.random.poisson(2)
        else:  # Tier 2 cities - more outages
            hist_outages = np.random.poisson(4)
        
        # Maintenance status
        maintenance_status = 1 if np.random.random() < 0.1 else 0
        
        # Feeder health (degrades in monsoon)
        base_health = 0.85
        if weather_data['rainfall'] > 20:
            base_health -= 0.1
        if timestamp.month in [6, 7, 8]:  # Peak monsoon
            base_health -= 0.05
        feeder_health = np.clip(base_health + np.random.normal(0, 0.1), 0.5, 0.95)
        
        # Transformer load
        transformer_load = min(0.95, load_factor + np.random.normal(0, 0.05))
        
        return {
            'load_factor': round(load_factor, 3),
            'voltage_stability': round(voltage_stability, 3),
            'historical_outages': int(hist_outages),
            'maintenance_status': maintenance_status,
            'feeder_health': round(feeder_health, 3),
            'transformer_load': round(transformer_load, 3)
        }
    
    def _calculate_outage_probability(self, weather_data, grid_data, city_info, timestamp):
        """Calculate realistic outage probability for Karnataka conditions."""
        risk_score = 0.0
        
        # Weather risk factors (major in Karnataka)
        if weather_data['rainfall'] > 25:  # Heavy rain
            risk_score += 0.3
        elif weather_data['rainfall'] > 10:
            risk_score += 0.15
        
        if weather_data['wind_speed'] > 40:  # High winds
            risk_score += 0.25
        elif weather_data['wind_speed'] > 25:
            risk_score += 0.1
        
        if weather_data['lightning_strikes'] > 3:  # Lightning
            risk_score += 0.2
        elif weather_data['lightning_strikes'] > 0:
            risk_score += 0.05
        
        if weather_data['storm_alert']:
            risk_score += 0.15
        
        # Grid risk factors
        if grid_data['load_factor'] > 0.9:  # Overload
            risk_score += 0.2
        elif grid_data['load_factor'] > 0.8:
            risk_score += 0.1
        
        if grid_data['voltage_stability'] < 0.8:  # Poor stability
            risk_score += 0.15
        
        if grid_data['maintenance_status']:
            risk_score += 0.1
        
        if grid_data['feeder_health'] < 0.7:
            risk_score += 0.1
        
        # Historical patterns
        risk_score += min(0.1, grid_data['historical_outages'] * 0.02)
        
        # City-specific adjustments
        if city_info['priority'] == 1:  # Better infrastructure
            risk_score *= 0.8
        
        # Seasonal adjustments
        if timestamp.month in [6, 7, 8]:  # Monsoon season
            risk_score *= 1.2
        
        # Time-based patterns
        if 6 <= timestamp.hour <= 8 or 18 <= timestamp.hour <= 20:  # Peak hours
            risk_score *= 1.1
        
        return min(0.95, max(0.01, risk_score))
    
    def _get_escom_zone(self, city_name):
        """Get the ESCOM zone for a city."""
        for escom, cities in self.escom_zones.items():
            if city_name in cities:
                return escom
        return 'BESCOM'  # Default


def download_real_karnataka_data():
    """Download and prepare real Karnataka power outage data."""
    loader = KarnatakaDataLoader()
    
    # Generate realistic dataset
    df = loader.generate_realistic_karnataka_data(years=5)
    
    print(f"Generated dataset with {len(df)} records")
    print(f"Cities covered: {df['city'].nunique()}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Outage rate: {df['outage_occurred'].mean():.2%}")
    
    return df


if __name__ == "__main__":
    # Generate the dataset
    data = download_real_karnataka_data()
    print("Karnataka dataset ready for training!")
