#!/usr/bin/env python3
"""
Demo script for the 24-Hour Power Outage Forecasting System.
This script demonstrates the system's capabilities with sample data.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Disable OneDNN optimizations for TensorFlow (if applicable)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.ensemble_model import EnsemblePredictor
from utils.feature_engineering import FeatureEngineer
from utils.cache_simple import CacheManager
from utils.geospatial import GeoSpatialProcessor
from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class PowerOutageDemo:
    """Demo class for the Power Outage Forecasting System."""
    
    def __init__(self):
        self.model = EnsemblePredictor()
        self.feature_engineer = FeatureEngineer()
        self.geo_processor = GeoSpatialProcessor()
        self.cache = CacheManager()
        
    async def initialize(self):
        """Initialize the demo system."""
        try:
            logger.info("Initializing demo system...")
            
            # Initialize cache
            await self.cache.initialize()
            
            # Load or create a demo model
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'trained')
            if os.path.exists(model_path):
                self.model.load_model(model_path)
                logger.info("Loaded pre-trained model")
            else:
                logger.info("No pre-trained model found. Run train_model.py first for better results.")
                
            logger.info("Demo system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize demo system: {str(e)}")
            raise
    
    def generate_sample_weather_data(self):
        """Generate sample weather data for demonstration."""
        logger.info("Generating sample weather data...")
        
        base_time = datetime.utcnow()
        
        # Generate 24-hour weather forecast
        weather_data = []
        for hour in range(24):
            time = base_time + timedelta(hours=hour)
            
            # Simulate a storm scenario
            if 6 <= hour <= 12:  # Storm period
                temp = 18 + np.random.normal(0, 2)
                humidity = 85 + np.random.normal(0, 5)
                wind_speed = 45 + np.random.normal(0, 8)
                rainfall = 25 + np.random.exponential(5)
                lightning = np.random.poisson(3)
                storm_alert = 1
            else:  # Normal weather
                temp = 25 + np.random.normal(0, 3)
                humidity = 60 + np.random.normal(0, 10)
                wind_speed = 15 + np.random.normal(0, 5)
                rainfall = np.random.exponential(2)
                lightning = np.random.poisson(0.5)
                storm_alert = 0
            
            weather_data.append({
                'timestamp': time.isoformat(),
                'temperature': round(temp, 1),
                'humidity': round(max(10, min(100, humidity)), 1),
                'wind_speed': round(max(0, wind_speed), 1),
                'rainfall': round(max(0, rainfall), 1),
                'lightning_strikes': int(lightning),
                'storm_alert': storm_alert
            })
        
        return weather_data
    
    def generate_sample_grid_data(self):
        """Generate sample grid data for demonstration."""
        logger.info("Generating sample grid data...")
        
        return {
            'load_factor': 0.85,  # High load
            'voltage_stability': 0.75,  # Moderate stability
            'historical_outages': 5,
            'maintenance_status': 0,  # No maintenance
            'feeder_health': 0.7,  # Fair health
            'grid_age': 15,
            'transformer_load': 0.8
        }
    
    async def demonstrate_prediction(self):
        """Demonstrate outage prediction."""
        print("\n" + "="*60)
        print("POWER OUTAGE PREDICTION DEMONSTRATION")
        print("="*60)
        
        try:
            # Generate sample data
            weather_data = self.generate_sample_weather_data()
            grid_data = self.generate_sample_grid_data()
            
            print("\nSample Input Data:")
            print("-" * 30)
            print("Weather Conditions (Next 6 hours):")
            for i in range(6):
                w = weather_data[i]
                print(f"  Hour {i+1}: {w['temperature']}°C, {w['humidity']}% humidity, "
                      f"{w['wind_speed']} km/h wind, {w['rainfall']}mm rain")
            
            print(f"\nGrid Status:")
            print(f"  Load Factor: {grid_data['load_factor']:.1%}")
            print(f"  Voltage Stability: {grid_data['voltage_stability']:.1%}")
            print(f"  Historical Outages: {grid_data['historical_outages']}")
            print(f"  Feeder Health: {grid_data['feeder_health']:.1%}")
            
            # Create prediction request
            prediction_request = {
                'location': {'latitude': -33.8688, 'longitude': 151.2093},  # Sydney
                'weather_data': weather_data,
                'grid_data': grid_data,
                'prediction_horizon': 24
            }
            
            # Make prediction
            print("\nMaking Prediction...")
            print("-" * 20)
            
            if hasattr(self.model, 'predict') and callable(getattr(self.model, 'predict')):
                # Use actual model if available
                prediction = await self.model.predict(prediction_request)
            else:
                # Generate mock prediction for demo
                prediction = self.generate_mock_prediction(weather_data, grid_data)
            
            # Display results
            self.display_prediction_results(prediction)
            
        except Exception as e:
            logger.error(f"Prediction demonstration failed: {str(e)}")
            print(f"Error during prediction: {str(e)}")
    
    def generate_mock_prediction(self, weather_data, grid_data):
        """Generate a mock prediction for demonstration."""
        
        # Calculate risk factors
        weather_risk = 0
        for w in weather_data[:6]:  # Next 6 hours
            if w['storm_alert']:
                weather_risk += 20
            if w['wind_speed'] > 40:
                weather_risk += 15
            if w['rainfall'] > 20:
                weather_risk += 10
            if w['lightning_strikes'] > 2:
                weather_risk += 5
        
        grid_risk = 0
        if grid_data['load_factor'] > 0.8:
            grid_risk += 15
        if grid_data['voltage_stability'] < 0.8:
            grid_risk += 10
        if grid_data['historical_outages'] > 3:
            grid_risk += 8
        if grid_data['feeder_health'] < 0.8:
            grid_risk += 12
        
        total_risk = min(weather_risk + grid_risk + np.random.normal(0, 5), 100)
        outage_probability = max(0, min(1, total_risk / 100))
        
        # Generate hourly predictions
        hourly_predictions = []
        for hour in range(24):
            # Risk decreases over time (uncertainty increases)
            hour_risk = total_risk * (1 - hour * 0.02)
            hour_prob = max(0, min(1, hour_risk / 100 + np.random.normal(0, 0.05)))
            
            hourly_predictions.append({
                'hour': hour + 1,
                'probability': round(hour_prob, 3),
                'risk_score': round(hour_risk, 1),
                'confidence': round(max(0.5, 1 - hour * 0.02), 2)
            })
        
        return {
            'overall_probability': round(outage_probability, 3),
            'risk_score': round(total_risk, 1),
            'confidence': 0.85,
            'hourly_predictions': hourly_predictions,
            'risk_factors': {
                'weather_risk': round(weather_risk, 1),
                'grid_risk': round(grid_risk, 1),
                'combined_risk': round(total_risk, 1)
            },
            'recommendations': self.generate_recommendations(total_risk),
            'prediction_timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_recommendations(self, risk_score):
        """Generate recommendations based on risk score."""
        recommendations = []
        
        if risk_score > 70:
            recommendations.extend([
                "HIGH RISK: Activate emergency response protocols",
                "Consider load shedding in high-risk areas",
                "Position repair crews for rapid response",
                "Issue public safety warnings"
            ])
        elif risk_score > 40:
            recommendations.extend([
                "MODERATE RISK: Monitor system closely",
                "Prepare maintenance crews for deployment",
                "Check backup systems and generators",
                "Communicate with critical infrastructure operators"
            ])
        else:
            recommendations.extend([
                "LOW RISK: Continue normal operations",
                "Maintain routine monitoring",
                "Standard preventive maintenance schedule"
            ])
        
        return recommendations
    
    def display_prediction_results(self, prediction):
        """Display prediction results in a formatted way."""
        print("\nPREDICTION RESULTS:")
        print("=" * 40)
        
        # Overall prediction
        prob = prediction['overall_probability']
        risk = prediction['risk_score']
        conf = prediction['confidence']
        
        print(f"Overall Outage Probability: {prob:.1%}")
        print(f"Risk Score: {risk:.1f}/100")
        print(f"Confidence Level: {conf:.1%}")
        
        # Risk level
        if risk > 70:
            risk_level = "🔴 HIGH RISK"
        elif risk > 40:
            risk_level = "🟡 MODERATE RISK"
        else:
            risk_level = "🟢 LOW RISK"
        
        print(f"Risk Level: {risk_level}")
        
        # Risk breakdown
        print(f"\nRisk Factor Breakdown:")
        factors = prediction['risk_factors']
        print(f"  Weather Risk: {factors['weather_risk']:.1f}/100")
        print(f"  Grid Risk: {factors['grid_risk']:.1f}/100")
        print(f"  Combined Risk: {factors['combined_risk']:.1f}/100")
        
        # Next 6 hours detail
        print(f"\nNext 6 Hours Forecast:")
        print("-" * 30)
        for hour_pred in prediction['hourly_predictions'][:6]:
            hour = hour_pred['hour']
            prob = hour_pred['probability']
            conf = hour_pred['confidence']
            print(f"  Hour {hour}: {prob:.1%} probability (confidence: {conf:.1%})")
        
        # Recommendations
        print(f"\nRecommendations:")
        print("-" * 20)
        for i, rec in enumerate(prediction['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nPrediction generated at: {prediction['prediction_timestamp']}")
    
    async def demonstrate_heatmap(self):
        """Demonstrate heatmap generation."""
        print("\n" + "="*60)
        print("RISK HEATMAP DEMONSTRATION")
        print("="*60)
        
        # Generate sample grid points
        grid_points = []
        base_lat, base_lon = -33.8688, 151.2093  # Sydney
        
        for i in range(5):
            for j in range(5):
                lat = base_lat + (i - 2) * 0.01
                lon = base_lon + (j - 2) * 0.01
                
                # Simulate risk scores
                distance_from_center = np.sqrt((i-2)**2 + (j-2)**2)
                base_risk = 30 + np.random.normal(0, 15)
                risk_score = max(0, min(100, base_risk + distance_from_center * 10))
                
                grid_points.append({
                    'latitude': lat,
                    'longitude': lon,
                    'risk_score': round(risk_score, 1),
                    'grid_id': f"GRID_{i}{j}"
                })
        
        print(f"Generated risk heatmap for {len(grid_points)} grid points:")
        print("-" * 50)
        
        # Display top risk areas
        sorted_points = sorted(grid_points, key=lambda x: x['risk_score'], reverse=True)
        
        print("Top 5 Highest Risk Areas:")
        for i, point in enumerate(sorted_points[:5], 1):
            risk_color = "🔴" if point['risk_score'] > 70 else "🟡" if point['risk_score'] > 40 else "🟢"
            print(f"  {i}. {point['grid_id']}: {point['risk_score']:.1f}/100 {risk_color}")
            print(f"     Location: ({point['latitude']:.4f}, {point['longitude']:.4f})")
        
        return grid_points
    
    async def demonstrate_advisory(self):
        """Demonstrate advisory generation."""
        print("\n" + "="*60)
        print("ADVISORY GENERATION DEMONSTRATION")
        print("="*60)
        
        # Generate sample advisory
        advisory = {
            'id': 'ADV-2024-001',
            'severity': 'HIGH',
            'title': 'Severe Weather Alert - Increased Outage Risk',
            'message': (
                "Due to approaching severe weather conditions with high winds (45+ km/h) and "
                "heavy rainfall (25+ mm/h) expected between 6:00 AM and 12:00 PM, there is an "
                "elevated risk of power outages in the following areas: Central Business District, "
                "Eastern Suburbs, and Northern Beaches. Load factor is currently at 85% with "
                "reduced voltage stability. Emergency crews are on standby."
            ),
            'affected_areas': [
                'Central Business District',
                'Eastern Suburbs', 
                'Northern Beaches'
            ],
            'recommendations': [
                'Avoid unnecessary electrical usage during peak hours',
                'Ensure backup power systems are functional',
                'Report outages immediately via emergency hotline',
                'Prepare for potential service interruptions'
            ],
            'valid_until': (datetime.utcnow() + timedelta(hours=12)).isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        print(f"Advisory ID: {advisory['id']}")
        print(f"Severity: {advisory['severity']}")
        print(f"Title: {advisory['title']}")
        print(f"\nMessage:")
        print(f"  {advisory['message']}")
        
        print(f"\nAffected Areas:")
        for area in advisory['affected_areas']:
            print(f"  • {area}")
        
        print(f"\nRecommendations:")
        for rec in advisory['recommendations']:
            print(f"  • {rec}")
        
        print(f"\nValid Until: {advisory['valid_until']}")
        
        return advisory
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.cache.close()
            logger.info("Demo cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


async def main():
    """Main demo function."""
    demo = PowerOutageDemo()
    
    try:
        # Initialize
        await demo.initialize()
        
        print("🔌 24-Hour Power Outage Forecasting System - DEMO")
        print("=" * 60)
        print("This demo showcases the system's key capabilities:")
        print("1. Outage probability prediction")
        print("2. Risk heatmap generation")
        print("3. Advisory generation")
        print("=" * 60)
        
        # Run demonstrations
        await demo.demonstrate_prediction()
        await demo.demonstrate_heatmap()
        await demo.demonstrate_advisory()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("To use the full system:")
        print("1. Train the model: python train_model.py")
        print("2. Start the API: python -m uvicorn src.api.main:app --reload")
        print("3. Access the web interface: http://localhost:8000")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"Demo failed: {str(e)}")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
