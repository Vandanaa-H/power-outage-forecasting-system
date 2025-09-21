#!/usr/bin/env python3
"""
Fix the trained model loading by creating a simple adapter.
"""

import joblib
import numpy as np
import pandas as pd

# Load the saved model
model_path = "models/karnataka_outage_model.joblib"
try:
    sklearn_model = joblib.load(model_path)
    print(f"✓ Loaded sklearn model: {type(sklearn_model).__name__}")
    
    # Test the model with sample data
    sample_features = np.array([[25, 60, 10, 0, 0, 0, 0.7, 0.9, 12, 0, 9, 2, 2, 0.7, 0.8, 10000000, 1, 1, 0, 0, 1]])
    prediction = sklearn_model.predict_proba(sample_features)
    print(f"✓ Test prediction: {prediction[0][1]*100:.1f}% outage risk")
    
    # Create a simple wrapper that can be imported anywhere
    class SimpleKarnatakaModel:
        """Simple wrapper for the trained Karnataka model."""
        
        def __init__(self, sklearn_model):
            self.model = sklearn_model
            self.feature_columns = [
                'temperature', 'humidity', 'wind_speed', 'rainfall', 'lightning_strikes', 'storm_alert',
                'load_factor', 'voltage_stability', 'hour', 'day_of_week', 'month', 'season',
                'historical_outages', 'transformer_load', 'feeder_health', 'population', 'priority',
                'monsoon', 'summer', 'city', 'escom'
            ]
        
        def predict_proba(self, features):
            """Predict outage probability."""
            return self.model.predict_proba(features)
        
        def predict(self, features):
            """Predict outage class."""
            return self.model.predict(features)
    
    # Save the wrapped model
    wrapped_model = SimpleKarnatakaModel(sklearn_model)
    
    # Save as a simple dictionary with the sklearn model
    model_dict = {
        'sklearn_model': sklearn_model,
        'feature_columns': wrapped_model.feature_columns,
        'model_type': 'VotingClassifier'
    }
    
    simple_model_path = "models/karnataka_simple_model.joblib"
    joblib.dump(model_dict, simple_model_path)
    print(f"✓ Saved simple model wrapper to: {simple_model_path}")
    
    # Test loading the simple model
    loaded_dict = joblib.load(simple_model_path)
    test_pred = loaded_dict['sklearn_model'].predict_proba(sample_features)
    print(f"✓ Verified simple model: {test_pred[0][1]*100:.1f}% outage risk")
    
    print("\n🎉 Model loading issue fixed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()