import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import xgboost as xgb
from sklearn.ensemble import VotingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import shap
import logging
from typing import Dict, List, Tuple, Any, Optional
import joblib
import os
from datetime import datetime, timedelta

from config.settings import ModelConfig
from src.utils.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class LSTMWeatherModel:
    """LSTM model for weather sequence prediction."""
    
    def __init__(self, sequence_length: int = 24, feature_count: int = 6):
        self.sequence_length = sequence_length
        self.feature_count = feature_count
        self.model = None
        self.scaler = StandardScaler()
        
    def build_model(self) -> Model:
        """Build LSTM model architecture."""
        inputs = layers.Input(shape=(self.sequence_length, self.feature_count))
        
        # LSTM layers with dropout
        x = layers.LSTM(128, return_sequences=True, dropout=0.2)(inputs)
        x = layers.LSTM(64, return_sequences=True, dropout=0.2)(x)
        x = layers.LSTM(32, dropout=0.2)(x)
        
        # Dense layers
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(32, activation='relu')(x)
        
        # Output layer - weather embeddings
        outputs = layers.Dense(16, activation='linear', name='weather_embeddings')(x)
        
        model = Model(inputs, outputs, name='lstm_weather_model')
        
        model.compile(
            optimizer=Adam(learning_rate=ModelConfig.LEARNING_RATE),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_sequences(self, weather_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequential data for LSTM training."""
        features = weather_data[ModelConfig.WEATHER_FEATURES].values
        features_scaled = self.scaler.fit_transform(features)
        
        X, y = [], []
        for i in range(len(features_scaled) - self.sequence_length):
            X.append(features_scaled[i:i + self.sequence_length])
            y.append(features_scaled[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(self, weather_data: pd.DataFrame, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train the LSTM model."""
        try:
            X, y = self.prepare_sequences(weather_data)
            
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
            
            self.model = self.build_model()
            
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=ModelConfig.EPOCHS,
                batch_size=ModelConfig.BATCH_SIZE,
                callbacks=callbacks,
                verbose=1
            )
            
            logger.info("LSTM weather model training completed")
            return {"history": history.history, "model": self.model}
            
        except Exception as e:
            logger.error(f"LSTM training error: {str(e)}")
            raise
    
    def predict_embeddings(self, weather_sequence: np.ndarray) -> np.ndarray:
        """Generate weather embeddings for ensemble model."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        weather_scaled = self.scaler.transform(weather_sequence)
        weather_reshaped = weather_scaled.reshape(1, self.sequence_length, self.feature_count)
        
        embeddings = self.model.predict(weather_reshaped)
        return embeddings.flatten()


class XGBoostEnsembleModel:
    """XGBoost model for final outage prediction."""
    
    def __init__(self):
        self.model = None
        self.feature_scaler = StandardScaler()
        self.feature_names = []
        self.explainer = None
        
    def build_model(self) -> xgb.XGBRegressor:
        """Build XGBoost model."""
        model = xgb.XGBRegressor(**ModelConfig.XGBOOST_PARAMS)
        return model
    
    def prepare_features(self, 
                        weather_embeddings: np.ndarray,
                        grid_features: Dict[str, Any],
                        temporal_features: Dict[str, Any]) -> np.ndarray:
        """Combine all features for final prediction."""
        
        # Grid features
        grid_array = np.array([
            grid_features.get('load_factor', 0),
            grid_features.get('voltage_stability', 1),
            grid_features.get('historical_outages', 0),
            grid_features.get('maintenance_status', 0),
            grid_features.get('feeder_health', 1)
        ])
        
        # Temporal features
        temporal_array = np.array([
            temporal_features.get('hour_of_day', 0),
            temporal_features.get('day_of_week', 0),
            temporal_features.get('month', 1),
            temporal_features.get('season', 0)
        ])
        
        # Combine all features
        combined_features = np.concatenate([
            weather_embeddings,
            grid_array,
            temporal_array
        ])
        
        return combined_features.reshape(1, -1)
    
    def train(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the XGBoost ensemble model."""
        try:
            # Prepare training features and targets
            X = training_data.drop(['outage_occurred', 'risk_score'], axis=1)
            y = training_data['risk_score']
            
            # Store feature names
            self.feature_names = list(X.columns)
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Build and train model
            self.model = self.build_model()
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            # Initialize SHAP explainer
            self.explainer = shap.Explainer(self.model, X_train)
            
            # Calculate metrics
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            logger.info(f"XGBoost model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            return {
                "train_score": train_score,
                "test_score": test_score,
                "feature_importance": dict(zip(self.feature_names, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"XGBoost training error: {str(e)}")
            raise
    
    def predict_with_explanation(self, features: np.ndarray) -> Dict[str, Any]:
        """Make prediction with SHAP explanation."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Scale features
        features_scaled = self.feature_scaler.transform(features)
        
        # Make prediction
        risk_score = self.model.predict(features_scaled)[0]
        
        # Calculate SHAP values
        shap_values = None
        feature_attribution = {}
        
        if self.explainer is not None:
            try:
                shap_values = self.explainer(features_scaled)
                feature_attribution = dict(zip(
                    self.feature_names, 
                    shap_values.values[0]
                ))
            except Exception as e:
                logger.warning(f"SHAP explanation failed: {str(e)}")
        
        # Calculate confidence interval (simplified)
        uncertainty = np.std([
            self.model.predict(features_scaled + np.random.normal(0, 0.1, features_scaled.shape))[0]
            for _ in range(10)
        ])
        
        confidence_interval = {
            'lower': max(0, risk_score - 1.96 * uncertainty),
            'upper': min(100, risk_score + 1.96 * uncertainty)
        }
        
        return {
            'risk_score': float(risk_score),
            'confidence_interval': confidence_interval,
            'explanation': {
                'shap_values': feature_attribution,
                'feature_importance': dict(zip(self.feature_names, self.model.feature_importances_))
            }
        }


class EnsemblePredictor:
    """Main ensemble model combining LSTM and XGBoost."""
    
    def __init__(self):
        self.lstm_model = LSTMWeatherModel()
        self.xgboost_model = XGBoostEnsembleModel()
        self.feature_engineer = FeatureEngineer()
        self.is_trained = False
        
    async def train(self, training_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Train the complete ensemble model."""
        try:
            logger.info("Starting ensemble model training")
            
            # Train LSTM on weather sequences
            lstm_results = self.lstm_model.train(training_data['weather_sequences'])
            
            # Train XGBoost on combined features
            xgboost_results = self.xgboost_model.train(training_data['combined_features'])
            
            self.is_trained = True
            
            training_results = {
                'lstm_results': lstm_results,
                'xgboost_results': xgboost_results,
                'training_timestamp': datetime.utcnow(),
                'model_version': '1.0.0'
            }
            
            logger.info("Ensemble model training completed successfully")
            return training_results
            
        except Exception as e:
            logger.error(f"Ensemble training error: {str(e)}")
            raise
    
    async def predict(self, input_data: Dict[str, Any], include_explanation: bool = True) -> Dict[str, Any]:
        """Make outage risk prediction."""
        try:
            if not self.is_trained:
                # In production, load pre-trained models
                logger.warning("Using mock prediction - model not trained")
                return self._mock_prediction(input_data, include_explanation)
            
            # Extract weather sequence
            weather_data = input_data['weather']
            weather_sequence = self._prepare_weather_sequence(weather_data)
            
            # Generate weather embeddings
            weather_embeddings = self.lstm_model.predict_embeddings(weather_sequence)
            
            # Engineer temporal features
            temporal_features = self.feature_engineer.extract_temporal_features(
                datetime.utcnow()
            )
            
            # Prepare combined features
            combined_features = self.xgboost_model.prepare_features(
                weather_embeddings,
                input_data['grid'],
                temporal_features
            )
            
            # Make final prediction
            if include_explanation:
                result = self.xgboost_model.predict_with_explanation(combined_features)
            else:
                features_scaled = self.xgboost_model.feature_scaler.transform(combined_features)
                risk_score = self.xgboost_model.model.predict(features_scaled)[0]
                result = {
                    'risk_score': float(risk_score),
                    'confidence_interval': {'lower': max(0, risk_score-10), 'upper': min(100, risk_score+10)}
                }
            
            # Add contributing factors
            result['contributing_factors'] = self._identify_contributing_factors(
                input_data, result.get('explanation', {})
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            # Return safe default
            return {
                'risk_score': 0.0,
                'confidence_interval': {'lower': 0.0, 'upper': 0.0},
                'contributing_factors': ["Prediction failed"]
            }
    
    def _prepare_weather_sequence(self, weather_data: Dict[str, Any]) -> np.ndarray:
        """Prepare weather data sequence for LSTM."""
        # In production, this would fetch historical weather data
        # For now, create a mock sequence
        sequence = []
        for i in range(24):  # 24-hour sequence
            sequence.append([
                weather_data.get('temperature', 25),
                weather_data.get('humidity', 60),
                weather_data.get('wind_speed', 10),
                weather_data.get('rainfall', 0),
                weather_data.get('lightning_strikes', 0),
                1 if weather_data.get('storm_alert', False) else 0
            ])
        
        return np.array(sequence)
    
    def _identify_contributing_factors(self, input_data: Dict[str, Any], explanation: Dict[str, Any]) -> List[str]:
        """Identify main contributing factors to risk."""
        factors = []
        
        weather = input_data.get('weather', {})
        grid = input_data.get('grid', {})
        
        # Weather factors
        if weather.get('rainfall', 0) > 25:
            factors.append("Heavy rainfall expected")
        if weather.get('wind_speed', 0) > 50:
            factors.append("Strong winds forecasted")
        if weather.get('lightning_strikes', 0) > 5:
            factors.append("High lightning activity")
        if weather.get('storm_alert', False):
            factors.append("Active storm warning")
        
        # Grid factors
        if grid.get('load_factor', 0) > 0.8:
            factors.append("High electrical demand")
        if grid.get('voltage_stability', 1) < 0.7:
            factors.append("Grid voltage instability")
        if grid.get('maintenance_status', False):
            factors.append("Equipment under maintenance")
        if grid.get('feeder_health', 1) < 0.6:
            factors.append("Poor feeder condition")
        
        return factors[:5]  # Return top 5 factors
    
    def _mock_prediction(self, input_data: Dict[str, Any], include_explanation: bool) -> Dict[str, Any]:
        """Generate mock prediction for demonstration."""
        weather = input_data.get('weather', {})
        grid = input_data.get('grid', {})
        
        # Simple rule-based mock prediction
        risk_score = 0.0
        
        # Weather contribution
        risk_score += weather.get('rainfall', 0) * 0.8
        risk_score += weather.get('wind_speed', 0) * 0.3
        risk_score += weather.get('lightning_strikes', 0) * 2.0
        if weather.get('storm_alert', False):
            risk_score += 20.0
        
        # Grid contribution
        risk_score += (1 - grid.get('voltage_stability', 1)) * 30
        risk_score += grid.get('load_factor', 0) * 25
        if grid.get('maintenance_status', False):
            risk_score += 15.0
        risk_score += (1 - grid.get('feeder_health', 1)) * 20
        
        # Cap at 100
        risk_score = min(100.0, max(0.0, risk_score))
        
        result = {
            'risk_score': risk_score,
            'confidence_interval': {
                'lower': max(0, risk_score - 10),
                'upper': min(100, risk_score + 10)
            }
        }
        
        if include_explanation:
            result['explanation'] = {
                'method': 'mock_prediction',
                'weather_contribution': weather.get('rainfall', 0) * 0.8 + weather.get('wind_speed', 0) * 0.3,
                'grid_contribution': (1 - grid.get('voltage_stability', 1)) * 30
            }
        
        result['contributing_factors'] = self._identify_contributing_factors(input_data, {})
        
        return result
    
    def save_model(self, model_path: str):
        """Save trained model to disk."""
        try:
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            
            # Save LSTM model
            if self.lstm_model.model is not None:
                self.lstm_model.model.save(os.path.join(model_path, 'lstm_model.h5'))
                joblib.dump(self.lstm_model.scaler, os.path.join(model_path, 'lstm_scaler.pkl'))
            
            # Save XGBoost model
            if self.xgboost_model.model is not None:
                self.xgboost_model.model.save_model(os.path.join(model_path, 'xgboost_model.json'))
                joblib.dump(self.xgboost_model.feature_scaler, os.path.join(model_path, 'feature_scaler.pkl'))
                joblib.dump(self.xgboost_model.feature_names, os.path.join(model_path, 'feature_names.pkl'))
            
            logger.info(f"Model saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Model saving error: {str(e)}")
            raise
    
    def load_model(self, model_path: str):
        """Load trained model from disk."""
        try:
            # Load LSTM model
            lstm_model_path = os.path.join(model_path, 'lstm_model.h5')
            if os.path.exists(lstm_model_path):
                self.lstm_model.model = tf.keras.models.load_model(lstm_model_path)
                self.lstm_model.scaler = joblib.load(os.path.join(model_path, 'lstm_scaler.pkl'))
            
            # Load XGBoost model
            xgb_model_path = os.path.join(model_path, 'xgboost_model.json')
            if os.path.exists(xgb_model_path):
                self.xgboost_model.model = xgb.XGBRegressor()
                self.xgboost_model.model.load_model(xgb_model_path)
                self.xgboost_model.feature_scaler = joblib.load(os.path.join(model_path, 'feature_scaler.pkl'))
                self.xgboost_model.feature_names = joblib.load(os.path.join(model_path, 'feature_names.pkl'))
                
                # Reinitialize SHAP explainer
                # Note: This requires training data, which we would need to store separately
            
            self.is_trained = True
            logger.info(f"Model loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Model loading error: {str(e)}")
            raise
