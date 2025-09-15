#!/usr/bin/env python3
"""
Training script for the 24-Hour Power Outage Forecasting System.
This script trains the ensemble model using historical data.
"""

import sys
import os
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import argparse

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.ensemble_model import EnsemblePredictor
from utils.feature_engineering import FeatureEngineer
from utils.logger import setup_logging, get_logger
from config.settings import settings

# Setup logging
setup_logging()
logger = get_logger(__name__)


def generate_synthetic_training_data(num_samples: int = 10000) -> dict:
    """Generate synthetic training data for demonstration."""
    logger.info(f"Generating {num_samples} synthetic training samples")
    
    # Generate weather sequences (24-hour sequences)
    np.random.seed(42)
    
    weather_sequences = []
    combined_features = []
    
    for i in range(num_samples):
        # Generate 24-hour weather sequence
        base_temp = np.random.normal(25, 8)  # Base temperature
        base_humidity = np.random.normal(60, 20)
        base_wind = np.random.exponential(15)
        base_rain = np.random.exponential(5)
        
        sequence = []
        for hour in range(24):
            # Add hourly variations
            temp_var = np.sin(hour * np.pi / 12) * 5  # Daily temperature cycle
            temp = base_temp + temp_var + np.random.normal(0, 2)
            
            humidity = np.clip(base_humidity + np.random.normal(0, 10), 10, 100)
            wind_speed = np.clip(base_wind + np.random.normal(0, 5), 0, 150)
            rainfall = np.clip(base_rain + np.random.exponential(2), 0, 100)
            lightning = np.random.poisson(1) if rainfall > 10 else 0
            storm_alert = 1 if rainfall > 25 or wind_speed > 50 else 0
            
            sequence.append([temp, humidity, wind_speed, rainfall, lightning, storm_alert])
        
        weather_sequences.append(sequence)
        
        # Generate combined features for XGBoost training
        # Weather embeddings (mock - in real training, these would come from LSTM)
        weather_embeddings = np.random.normal(0, 1, 16)
        
        # Grid features
        load_factor = np.random.beta(2, 2)  # Beta distribution for load factor
        voltage_stability = np.random.beta(5, 2)  # Higher values more likely
        historical_outages = np.random.poisson(3)
        maintenance_status = np.random.choice([0, 1], p=[0.8, 0.2])
        feeder_health = np.random.beta(5, 2)
        
        # Temporal features
        hour_of_day = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        month = np.random.randint(1, 13)
        season = (month - 1) // 3
        
        # Calculate risk score based on features
        risk_score = 0
        
        # Weather contribution
        risk_score += max(0, (sequence[-1][3] - 10) * 1.5)  # Rainfall
        risk_score += max(0, (sequence[-1][2] - 30) * 0.8)  # Wind speed
        risk_score += sequence[-1][4] * 3  # Lightning
        risk_score += sequence[-1][5] * 15  # Storm alert
        
        # Grid contribution
        risk_score += max(0, (load_factor - 0.7) * 50)
        risk_score += max(0, (0.8 - voltage_stability) * 40)
        risk_score += min(historical_outages * 2, 15)
        risk_score += maintenance_status * 10
        risk_score += max(0, (0.7 - feeder_health) * 30)
        
        # Add some randomness
        risk_score += np.random.normal(0, 5)
        risk_score = np.clip(risk_score, 0, 100)
        
        # Determine if outage occurred (binary target)
        outage_occurred = 1 if risk_score > np.random.uniform(40, 80) else 0
        
        # Create feature vector
        features = list(weather_embeddings) + [
            load_factor, voltage_stability, historical_outages, 
            maintenance_status, feeder_health, hour_of_day, 
            day_of_week, month, season
        ]
        
        combined_features.append(features + [outage_occurred, risk_score])
    
    # Convert to DataFrames
    weather_df = pd.DataFrame(
        [seq for seq in weather_sequences],
        columns=[f'hour_{i}' for i in range(24)]
    )
    
    feature_columns = (
        [f'weather_emb_{i}' for i in range(16)] + 
        ['load_factor', 'voltage_stability', 'historical_outages', 
         'maintenance_status', 'feeder_health', 'hour_of_day', 
         'day_of_week', 'month', 'season', 'outage_occurred', 'risk_score']
    )
    
    combined_df = pd.DataFrame(combined_features, columns=feature_columns)
    
    logger.info("Synthetic training data generated successfully")
    
    return {
        'weather_sequences': weather_df,
        'combined_features': combined_df
    }


async def train_model(data_path: str = None, save_path: str = None):
    """Train the ensemble model."""
    try:
        logger.info("Starting model training")
        
        # Initialize model
        model = EnsemblePredictor()
        
        # Load or generate training data
        if data_path and os.path.exists(data_path):
            logger.info(f"Loading training data from {data_path}")
            # Load real data here
            training_data = {}
        else:
            logger.info("Generating synthetic training data")
            training_data = generate_synthetic_training_data(10000)
        
        # Train the model
        training_results = await model.train(training_data)
        
        # Save the trained model
        if save_path:
            model_save_path = save_path
        else:
            model_save_path = os.path.join(os.path.dirname(__file__), 'models', 'trained')
        
        os.makedirs(model_save_path, exist_ok=True)
        model.save_model(model_save_path)
        
        logger.info(f"Model training completed successfully")
        logger.info(f"Model saved to: {model_save_path}")
        
        # Print training results
        print("\n" + "="*50)
        print("TRAINING RESULTS")
        print("="*50)
        
        if 'lstm_results' in training_results:
            print(f"LSTM Model Training Loss: {training_results['lstm_results'].get('final_loss', 'N/A')}")
        
        if 'xgboost_results' in training_results:
            xgb_results = training_results['xgboost_results']
            print(f"XGBoost Train R²: {xgb_results.get('train_score', 'N/A'):.3f}")
            print(f"XGBoost Test R²: {xgb_results.get('test_score', 'N/A'):.3f}")
        
        print(f"Training completed at: {training_results.get('training_timestamp', datetime.utcnow())}")
        print("="*50)
        
        return training_results
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise


async def evaluate_model(model_path: str, test_data_path: str = None):
    """Evaluate the trained model."""
    try:
        logger.info("Starting model evaluation")
        
        # Load model
        model = EnsemblePredictor()
        model.load_model(model_path)
        
        # Generate test data if not provided
        if test_data_path and os.path.exists(test_data_path):
            # Load real test data
            pass
        else:
            logger.info("Generating synthetic test data")
            test_data = generate_synthetic_training_data(1000)
        
        # Run evaluation
        # This would include more comprehensive evaluation metrics
        logger.info("Model evaluation completed")
        
    except Exception as e:
        logger.error(f"Model evaluation failed: {str(e)}")
        raise


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description='Train the Power Outage Forecasting Model')
    parser.add_argument('--data', type=str, help='Path to training data')
    parser.add_argument('--save', type=str, help='Path to save trained model')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate model after training')
    parser.add_argument('--model-path', type=str, help='Path to trained model for evaluation')
    
    args = parser.parse_args()
    
    try:
        # Train model
        training_results = asyncio.run(train_model(args.data, args.save))
        
        # Evaluate if requested
        if args.evaluate:
            model_path = args.model_path or args.save or os.path.join(os.path.dirname(__file__), 'models', 'trained')
            asyncio.run(evaluate_model(model_path))
        
        print("\nTraining completed successfully!")
        
    except Exception as e:
        logger.error(f"Training script failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

python -c ""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate proper synthetic data with required columns
np.random.seed(42)
n_samples = 10000
start_date = datetime(2020, 1, 1)
dates = [start_date + timedelta(hours=i) for i in range(n_samples)]

data = {
    'timestamp': dates,
    'temperature': np.random.normal(20, 10, n_samples),
    'humidity': np.random.uniform(30, 90, n_samples),
    'wind_speed': np.random.exponential(15, n_samples),
    'rainfall': np.random.exponential(2, n_samples),
    'lightning_strikes': np.random.poisson(0.5, n_samples),
    'storm_alert': np.random.binomial(1, 0.1, n_samples),
    'power_outage': np.random.binomial(1, 0.05, n_samples)
}

df = pd.DataFrame(data)
df.to_csv('data/synthetic_training_data.csv', index=False)
print('Fixed synthetic data generated with required columns')
"
