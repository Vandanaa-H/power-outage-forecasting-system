#!/usr/bin/env python3
"""
Karnataka Power Outage Forecasting - Real ML Training Pipeline
Trains LSTM + XGBoost ensemble specifically for Karnataka data
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# ML imports
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb

# Deep learning
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Explainability
import shap

from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class KarnatakaPowerOutagePredictor:
    """Real ML pipeline for Karnataka power outage prediction."""
    
    def __init__(self):
        self.lstm_model = None
        self.xgb_model = None
        self.scaler = None
        self.feature_columns = None
        self.target_column = 'outage_occurred'
        
        # Karnataka-specific features
        self.weather_features = [
            'temperature', 'humidity', 'wind_speed', 'rainfall', 
            'lightning_strikes', 'storm_alert'
        ]
        
        self.grid_features = [
            'load_factor', 'voltage_stability', 'historical_outages',
            'maintenance_status', 'feeder_health', 'transformer_load'
        ]
        
        self.temporal_features = [
            'hour_of_day', 'day_of_week', 'month', 'season'
        ]
        
        self.contextual_features = [
            'priority_tier', 'population', 'is_monsoon', 'is_summer'
        ]
    
    def load_karnataka_data(self):
        """Load the generated Karnataka dataset."""
        data_path = Path("data/karnataka_power_outage_dataset.csv")
        
        if not data_path.exists():
            logger.error("Karnataka dataset not found. Run data/karnataka_data_loader.py first")
            raise FileNotFoundError("Karnataka dataset not found")
        
        logger.info("Loading Karnataka power outage dataset...")
        df = pd.read_csv(data_path)
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"Loaded {len(df)} records from {df['timestamp'].min()} to {df['timestamp'].max()}")
        logger.info(f"Cities: {list(df['city'].unique())}")
        logger.info(f"Outage rate: {df['outage_occurred'].mean():.2%}")
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for ML training."""
        logger.info("Preparing features for Karnataka dataset...")
        
        # Combine all feature columns
        all_features = (self.weather_features + self.grid_features + 
                       self.temporal_features + self.contextual_features)
        
        # Encode categorical features
        le_city = LabelEncoder()
        df['city_encoded'] = le_city.fit_transform(df['city'])
        
        le_escom = LabelEncoder()
        df['escom_encoded'] = le_escom.fit_transform(df['escom_zone'])
        
        # Add encoded features
        all_features.extend(['city_encoded', 'escom_encoded'])
        
        # Create feature matrix
        X = df[all_features].copy()
        y = df[self.target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        self.feature_columns = all_features
        logger.info(f"Prepared {len(all_features)} features: {all_features}")
        
        return X, y, df
    
    def create_lstm_sequences(self, df, sequence_length=24):
        """Create LSTM sequences for weather patterns."""
        logger.info(f"Creating LSTM sequences with length {sequence_length}")
        
        sequences = []
        targets = []
        
        # Group by city for sequence creation
        for city in df['city'].unique():
            city_data = df[df['city'] == city].sort_values('timestamp')
            
            # Create sequences for this city
            for i in range(len(city_data) - sequence_length):
                # Weather sequence (past 24 hours)
                weather_seq = city_data[self.weather_features].iloc[i:i+sequence_length].values
                
                # Target (next hour outage)
                target = city_data[self.target_column].iloc[i+sequence_length]
                
                sequences.append(weather_seq)
                targets.append(target)
        
        X_seq = np.array(sequences)
        y_seq = np.array(targets)
        
        logger.info(f"Created {len(sequences)} sequences of shape {X_seq.shape}")
        return X_seq, y_seq
    
    def train_lstm_model(self, X_seq, y_seq):
        """Train LSTM model for weather sequence analysis."""
        logger.info("Training LSTM model for weather patterns...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_seq, test_size=0.2, random_state=42, stratify=y_seq
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1]))
        X_train_scaled = X_train_scaled.reshape(X_train.shape)
        
        X_test_scaled = self.scaler.transform(X_test.reshape(-1, X_test.shape[-1]))
        X_test_scaled = X_test_scaled.reshape(X_test.shape)
        
        # Build LSTM model
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            BatchNormalization(),
            
            Dense(16, activation='relu'),
            Dropout(0.1),
            
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(patience=5, factor=0.5, verbose=1)
        ]
        
        # Train model
        history = model.fit(
            X_train_scaled, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test_scaled, y_test),
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        test_loss, test_acc, test_prec, test_rec = model.evaluate(X_test_scaled, y_test, verbose=0)
        logger.info(f"LSTM Test Results - Loss: {test_loss:.4f}, Accuracy: {test_acc:.4f}")
        logger.info(f"LSTM Precision: {test_prec:.4f}, Recall: {test_rec:.4f}")
        
        self.lstm_model = model
        return history
    
    def train_xgboost_model(self, X, y):
        """Train XGBoost model for tabular features."""
        logger.info("Training XGBoost model for grid and contextual features...")
        
        # Split data with time series consideration
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train XGBoost
        xgb_params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'early_stopping_rounds': 20
        }
        
        self.xgb_model = xgb.XGBClassifier(**xgb_params)
        
        # Train with early stopping
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=True
        )
        
        # Evaluate
        y_pred = self.xgb_model.predict(X_test)
        y_pred_proba = self.xgb_model.predict_proba(X_test)[:, 1]
        
        auc_score = roc_auc_score(y_test, y_pred_proba)
        logger.info(f"XGBoost AUC Score: {auc_score:.4f}")
        
        # Classification report
        logger.info("XGBoost Classification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        return self.xgb_model
    
    def generate_shap_explanations(self, X_sample):
        """Generate SHAP explanations for model predictions."""
        logger.info("Generating SHAP explanations...")
        
        # Create explainer for XGBoost
        explainer = shap.TreeExplainer(self.xgb_model)
        shap_values = explainer.shap_values(X_sample.iloc[:100])  # Sample for speed
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': np.abs(shap_values).mean(0)
        }).sort_values('importance', ascending=False)
        
        logger.info("Top 10 Most Important Features:")
        for _, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return shap_values, feature_importance
    
    def save_models(self, save_dir="models/karnataka_trained"):
        """Save trained models."""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save LSTM model
        if self.lstm_model:
            lstm_path = save_path / "lstm_weather_model.h5"
            self.lstm_model.save(lstm_path)
            logger.info(f"Saved LSTM model to {lstm_path}")
        
        # Save XGBoost model
        if self.xgb_model:
            xgb_path = save_path / "xgboost_model.json"
            self.xgb_model.save_model(xgb_path)
            logger.info(f"Saved XGBoost model to {xgb_path}")
        
        # Save scaler
        if self.scaler:
            import joblib
            scaler_path = save_path / "feature_scaler.pkl"
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Saved scaler to {scaler_path}")
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'weather_features': self.weather_features,
            'grid_features': self.grid_features,
            'temporal_features': self.temporal_features,
            'contextual_features': self.contextual_features,
            'training_timestamp': datetime.now().isoformat()
        }
        
        import json
        metadata_path = save_path / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata to {metadata_path}")


def main():
    """Main training pipeline for Karnataka power outage prediction."""
    try:
        logger.info("Starting Karnataka Power Outage Forecasting Training")
        
        # Initialize predictor
        predictor = KarnatakaPowerOutagePredictor()
        
        # Load data
        df = predictor.load_karnataka_data()
        
        # Prepare features
        X, y, df = predictor.prepare_features(df)
        
        # Create LSTM sequences
        X_seq, y_seq = predictor.create_lstm_sequences(df)
        
        # Train LSTM model
        lstm_history = predictor.train_lstm_model(X_seq, y_seq)
        
        # Train XGBoost model
        xgb_model = predictor.train_xgboost_model(X, y)
        
        # Generate explanations
        shap_values, feature_importance = predictor.generate_shap_explanations(X)
        
        # Save models
        predictor.save_models()
        
        print("\n" + "="*60)
        print("KARNATAKA POWER OUTAGE FORECASTING - TRAINING COMPLETE")
        print("="*60)
        print(f"Dataset: {len(df)} records from Karnataka")
        print(f"Cities covered: {df['city'].nunique()}")
        print(f"Time range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
        print(f"Outage rate: {df['outage_occurred'].mean():.2%}")
        print("\nModel Architecture:")
        print("  - LSTM: Weather sequence analysis (24-hour patterns)")
        print("  - XGBoost: Grid and contextual features")
        print("  - SHAP: Explainability and feature importance")
        print("\nTop 5 Predictive Features:")
        for i, (_, row) in enumerate(feature_importance.head(5).iterrows(), 1):
            print(f"  {i}. {row['feature']}")
        print(f"\nModels saved to: models/karnataka_trained/")
        print("="*60)
        
        return {
            'status': 'success',
            'records_trained': len(df),
            'cities': df['city'].nunique(),
            'outage_rate': df['outage_occurred'].mean(),
            'model_performance': {
                'lstm_accuracy': lstm_history.history['val_accuracy'][-1],
                'xgb_auc': roc_auc_score(y[int(len(y)*0.8):], 
                                       xgb_model.predict_proba(X[int(len(X)*0.8):])[:, 1])
            }
        }
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
